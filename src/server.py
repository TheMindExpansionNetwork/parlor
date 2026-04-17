"""MindBotz - on-device, real-time multimodal AI (voice + vision)."""

import asyncio
import base64
import json
import os
import re
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import tts

try:
    import litert_lm
except ModuleNotFoundError:
    litert_lm = None

HF_REPO = "litert-community/gemma-4-E2B-it-litert-lm"
HF_FILENAME = "gemma-4-E2B-it.litertlm"
ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_CANDIDATES = (
    "Gemma-4-E2B-it-abliterated.litertlm",
    "gemma-4-E2B-it.litertlm",
)


def load_env_file(path: Path) -> None:
    """Load a minimal .env file without requiring python-dotenv."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def resolve_path(raw_path: str) -> Path:
    path = Path(os.path.expandvars(os.path.expanduser(raw_path)))
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path.resolve()


def find_local_model() -> Path | None:
    models_dir = ROOT_DIR / "models"
    for filename in DEFAULT_MODEL_CANDIDATES:
        candidate = models_dir / filename
        if candidate.exists():
            return candidate.resolve()

    litert_models = sorted(models_dir.glob("*.litertlm"))
    if litert_models:
        return litert_models[0].resolve()
    return None


def runtime_support_error() -> str:
    if sys.platform == "win32":
        return (
            "LiteRT-LM does not currently publish native Windows wheels, so this app "
            "cannot run on win_amd64 yet. Use the same repo on macOS, Linux, or a "
            "Linux environment that can install litert-lm."
        )
    return (
        "litert-lm is not installed. Run `uv sync` on a supported platform before "
        "starting the server."
    )


def resolve_model_path() -> str:
    path = os.environ.get("MODEL_PATH", "")
    if path:
        resolved = resolve_path(path)
        if not resolved.exists():
            raise FileNotFoundError(f"MODEL_PATH does not exist: {resolved}")
        return str(resolved)

    local_model = find_local_model()
    if local_model:
        print(f"Using local model: {local_model}")
        return str(local_model)

    from huggingface_hub import hf_hub_download

    print(f"Downloading {HF_REPO}/{HF_FILENAME} (first run only)...")
    return hf_hub_download(repo_id=HF_REPO, filename=HF_FILENAME)


load_env_file(ROOT_DIR / ".env")
MODEL_PATH = resolve_model_path()
SYSTEM_PROMPT = (
    "You are a friendly, conversational AI assistant. The user is talking to you "
    "through a microphone and showing you their camera. "
    "You MUST always use the respond_to_user tool to reply. "
    "First transcribe exactly what the user said, then write your response."
)

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

engine = None
tts_backend = None


def load_models():
    global engine, tts_backend
    if litert_lm is None:
        raise RuntimeError(runtime_support_error())

    print(f"Loading Gemma 4 E2B from {MODEL_PATH}...")
    engine = litert_lm.Engine(
        MODEL_PATH,
        backend=litert_lm.Backend.GPU,
        vision_backend=litert_lm.Backend.GPU,
        audio_backend=litert_lm.Backend.CPU,
    )
    engine.__enter__()
    print("Engine loaded.")

    tts_backend = tts.load()


@asynccontextmanager
async def lifespan(app):
    await asyncio.get_event_loop().run_in_executor(None, load_models)
    yield


app = FastAPI(lifespan=lifespan)


def split_sentences(text: str) -> list[str]:
    """Split text into sentences for streaming TTS."""
    parts = SENTENCE_SPLIT_RE.split(text.strip())
    return [s.strip() for s in parts if s.strip()]


@app.get("/")
async def root():
    return HTMLResponse(content=(Path(__file__).parent / "index.html").read_text())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    tool_result = {}

    def respond_to_user(transcription: str, response: str) -> str:
        """Respond to the user's voice message."""
        tool_result["transcription"] = transcription
        tool_result["response"] = response
        return "OK"

    conversation = engine.create_conversation(
        messages=[{"role": "system", "content": SYSTEM_PROMPT}],
        tools=[respond_to_user],
    )
    conversation.__enter__()

    interrupted = asyncio.Event()
    msg_queue = asyncio.Queue()

    async def receiver():
        try:
            while True:
                raw = await ws.receive_text()
                msg = json.loads(raw)
                if msg.get("type") == "interrupt":
                    interrupted.set()
                    print("Client interrupted")
                else:
                    await msg_queue.put(msg)
        except WebSocketDisconnect:
            await msg_queue.put(None)

    recv_task = asyncio.create_task(receiver())

    try:
        while True:
            msg = await msg_queue.get()
            if msg is None:
                break

            interrupted.clear()

            content = []
            preset = (msg.get("preset") or "balanced").lower()
            style_prompt = (msg.get("style_prompt") or "").strip()
            if msg.get("audio"):
                content.append({"type": "audio", "blob": msg["audio"]})
            if msg.get("image"):
                content.append({"type": "image", "blob": msg["image"]})

            if msg.get("audio") and msg.get("image"):
                content.append(
                    {
                        "type": "text",
                        "text": "The user just spoke to you (audio) while showing their camera (image). Respond to what they said, referencing what you see if relevant.",
                    }
                )
            elif msg.get("audio"):
                content.append({"type": "text", "text": "The user just spoke to you. Respond to what they said."})
            elif msg.get("image"):
                content.append({"type": "text", "text": "The user is showing you their camera. Describe what you see."})
            else:
                content.append({"type": "text", "text": msg.get("text", "Hello!")})

            preset_instructions = {
                "balanced": "Keep responses concise, clear, and natural.",
                "coach": "Act like a supportive speaking coach. Be encouraging and gently correct mistakes when useful.",
                "fun": "Add light, playful energy. Keep it helpful first, then fun.",
                "fast": "Prioritize speed. Answer briefly in 1-2 short sentences unless detail is requested.",
            }
            content.append(
                {
                    "type": "text",
                    "text": f"Assistant preset: {preset}. {preset_instructions.get(preset, preset_instructions['balanced'])}",
                }
            )
            if style_prompt:
                content.append(
                    {
                        "type": "text",
                        "text": f"Additional user preference: {style_prompt}",
                    }
                )

            t0 = time.time()
            tool_result.clear()
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: conversation.send_message({"role": "user", "content": content})
            )
            llm_time = time.time() - t0

            if tool_result:
                strip = lambda s: s.replace('<|"|>', "").strip()
                transcription = strip(tool_result.get("transcription", ""))
                text_response = strip(tool_result.get("response", ""))
                print(f"LLM ({llm_time:.2f}s) [tool] heard: {transcription!r} -> {text_response}")
            else:
                transcription = None
                text_response = response["content"][0]["text"]
                print(f"LLM ({llm_time:.2f}s) [no tool]: {text_response}")

            if interrupted.is_set():
                print("Interrupted after LLM, skipping response")
                continue

            reply = {"type": "text", "text": text_response, "llm_time": round(llm_time, 2)}
            if transcription:
                reply["transcription"] = transcription
            await ws.send_text(json.dumps(reply))

            if interrupted.is_set():
                print("Interrupted before TTS, skipping audio")
                continue

            sentences = split_sentences(text_response)
            if not sentences:
                sentences = [text_response]

            tts_start = time.time()

            await ws.send_text(
                json.dumps(
                    {
                        "type": "audio_start",
                        "sample_rate": tts_backend.sample_rate,
                        "sentence_count": len(sentences),
                    }
                )
            )

            for i, sentence in enumerate(sentences):
                if interrupted.is_set():
                    print(f"Interrupted during TTS (sentence {i + 1}/{len(sentences)})")
                    break

                pcm = await asyncio.get_event_loop().run_in_executor(
                    None, lambda s=sentence: tts_backend.generate(s)
                )

                if interrupted.is_set():
                    break

                pcm_int16 = (pcm * 32767).clip(-32768, 32767).astype(np.int16)
                await ws.send_text(
                    json.dumps(
                        {
                            "type": "audio_chunk",
                            "audio": base64.b64encode(pcm_int16.tobytes()).decode(),
                            "index": i,
                        }
                    )
                )

            tts_time = time.time() - tts_start
            print(f"TTS ({tts_time:.2f}s): {len(sentences)} sentences")

            if not interrupted.is_set():
                await ws.send_text(
                    json.dumps(
                        {
                            "type": "audio_end",
                            "tts_time": round(tts_time, 2),
                        }
                    )
                )

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        recv_task.cancel()
        conversation.__exit__(None, None, None)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
