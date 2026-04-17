# 🧠⚡ MindBotz — On‑Device AI, No Cloud Leash

Talk to an AI that **sees**, **hears**, and **responds in real time**—all on your own hardware.
No cloud dependency, no token meter anxiety, no black-box server in the middle.

MindBotz uses [Gemma 4 E2B](https://huggingface.co/google/gemma-4-E2B-it) for speech+vision understanding, and [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) for natural text-to-speech.

https://github.com/user-attachments/assets/cb0ffb2e-f84f-48e7-872c-c5f7b5c6d51f

> **Research preview:** this is still an experiment. Fast, fun, and useful—but not “finished.”

---

## Why this exists

I’m [self-hosting a free voice AI](https://www.fikrikarim.com/bule-ai-initial-release/) for English learners with hundreds of MAU. The challenge is sustainability.

The long-term answer is simple: **run local, run cheap, run private**.

Six months ago this class of experience needed huge GPUs for real-time usage. Today, smaller models plus efficient runtimes make this practical on machines like an M3 Pro—and eventually, phones.

---

## How it works

```text
Browser (mic + camera)
    │
    │  WebSocket (audio PCM + JPEG frames)
    ▼
FastAPI server
    ├── Gemma 4 E2B via LiteRT-LM (GPU)  →  understands speech + vision
    └── Kokoro TTS (MLX on Mac, ONNX on Linux)  →  speaks back
    │
    │  WebSocket (streamed audio chunks)
    ▼
Browser (playback + transcript)
```

- **Voice Activity Detection** in-browser ([Silero VAD](https://github.com/ricky0123/vad))
- **Barge-in support** (interrupt mid-sentence)
- **Sentence-level TTS streaming** (audio starts before full text is done)

---

## Requirements

- Python 3.12+
- macOS (Apple Silicon), Linux, or Windows 11
- ~3 GB RAM available for model runtime

---

## Quick start (macOS / Linux)

```bash
git clone https://github.com/fikrikarim/parlor.git
cd parlor

# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

cd src
uv sync
uv run server.py
```

Then open [http://localhost:8000](http://localhost:8000), allow mic/camera, and start talking.

---

## Quick start (Windows)

### One-time setup

1. Install Python 3.12+.
2. Install `uv`:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. Clone this repo.

### Run with one command

From the project root, double-click `scripts\\start_windows.bat` (or run it in `cmd`).

The script will:
- `cd` into `src`
- run `uv sync`
- launch the app with `uv run server.py`

---

## What this fork adds

- **MindBotz rebrand**
- **Conversation presets**: `Balanced`, `Coach`, `Fun`, `Fast`
- **Quick style chips**: `Simple`, `Challenge`, `Emoji`
- **Fast mode optimization**: smaller camera frames + lower JPEG quality for lower latency

Models auto-download on first run (~2.6 GB for Gemma 4 E2B + TTS files).

---

## Product planning and brainstorm docs

All roadmap ideas, launch planning, branch workflow notes, and merge-conflict recovery steps now live in:

- [`docs/brainstorm-and-launch-plan.md`](docs/brainstorm-and-launch-plan.md)

This keeps the main README focused on setup + running the project.
