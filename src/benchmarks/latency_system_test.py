"""System latency test for the MindBotz WebSocket endpoint.

Start the app first:
    uv run python server.py

Then run this test from src/:
    uv run python benchmarks/latency_system_test.py

The test sends repeatable text/audio/image payloads and asserts p95/mean latency
thresholds so regressions fail fast in CI or local checks.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import io
import json
import os
import statistics
import time
import wave
from dataclasses import dataclass

import numpy as np
import websockets
from PIL import Image

SERVER_URL = os.environ.get("SERVER_URL", "ws://localhost:8000/ws")


@dataclass
class LatencyResult:
    text_recv_s: float
    total_s: float
    llm_s: float
    tts_s: float


@dataclass
class ScenarioSummary:
    name: str
    runs: int
    mean_text_s: float
    p95_text_s: float
    mean_total_s: float
    p95_total_s: float


def make_wav_b64(duration_s: float, sample_rate: int = 16000) -> str:
    samples = np.sin(2 * np.pi * 440 * np.arange(int(sample_rate * duration_s)) / sample_rate)
    pcm = (samples * 32767).clip(-32768, 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm.tobytes())

    return base64.b64encode(buf.getvalue()).decode()


def make_jpg_b64(width: int = 320, height: int = 240) -> str:
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


def percentile(values: list[float], pct: float) -> float:
    if not values:
        raise ValueError("values must be non-empty")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * (pct / 100)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


async def run_turn(ws: websockets.ClientConnection, payload: dict, timeout_s: float) -> LatencyResult:
    t0 = time.time()
    await ws.send(json.dumps(payload))

    text_recv_s: float | None = None
    llm_s = 0.0
    tts_s = 0.0

    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout_s)
        msg = json.loads(raw)

        if msg["type"] == "text":
            text_recv_s = time.time() - t0
            llm_s = float(msg.get("llm_time") or 0.0)
        elif msg["type"] == "audio_end":
            tts_s = float(msg.get("tts_time") or 0.0)
            break

    return LatencyResult(
        text_recv_s=round(text_recv_s or 0.0, 3),
        total_s=round(time.time() - t0, 3),
        llm_s=round(llm_s, 3),
        tts_s=round(tts_s, 3),
    )


async def execute_scenario(
    name: str,
    payload: dict,
    runs: int,
    warmup: int,
    timeout_s: float,
    verbose: bool,
) -> tuple[ScenarioSummary, list[LatencyResult]]:
    results: list[LatencyResult] = []

    async with websockets.connect(SERVER_URL) as ws:
        for i in range(warmup + runs):
            result = await run_turn(ws, payload, timeout_s)
            if i < warmup:
                continue
            results.append(result)
            if verbose:
                idx = i - warmup + 1
                print(
                    f"  run {idx:02d}: text={result.text_recv_s:.2f}s total={result.total_s:.2f}s "
                    f"(llm={result.llm_s:.2f}s, tts={result.tts_s:.2f}s)"
                )

    text_values = [r.text_recv_s for r in results]
    total_values = [r.total_s for r in results]

    summary = ScenarioSummary(
        name=name,
        runs=len(results),
        mean_text_s=statistics.mean(text_values),
        p95_text_s=percentile(text_values, 95),
        mean_total_s=statistics.mean(total_values),
        p95_total_s=percentile(total_values, 95),
    )
    return summary, results


def print_summary(summary: ScenarioSummary) -> None:
    print(
        f"{summary.name:<18} runs={summary.runs:<2} "
        f"text mean={summary.mean_text_s:>5.2f}s p95={summary.p95_text_s:>5.2f}s | "
        f"total mean={summary.mean_total_s:>5.2f}s p95={summary.p95_total_s:>5.2f}s"
    )


async def main() -> int:
    parser = argparse.ArgumentParser(description="System latency test for the /ws endpoint")
    parser.add_argument("--runs", type=int, default=5, help="Measured runs per scenario")
    parser.add_argument("--warmup", type=int, default=1, help="Warmup runs per scenario")
    parser.add_argument("--timeout", type=float, default=60.0, help="Timeout per run (seconds)")
    parser.add_argument("--max-text-p95", type=float, default=8.0, help="Fail if text latency p95 exceeds this")
    parser.add_argument("--max-total-p95", type=float, default=14.0, help="Fail if total latency p95 exceeds this")
    parser.add_argument("--verbose", action="store_true", help="Print each measured run")
    args = parser.parse_args()

    audio_2s = make_wav_b64(2.0)
    image = make_jpg_b64()

    scenarios = [
        ("text-only", {"text": "In one sentence, explain why sunsets are red."}),
        ("audio-only", {"audio": audio_2s}),
        ("audio+image", {"audio": audio_2s, "image": image}),
    ]

    print("=" * 92)
    print(f"SYSTEM LATENCY TEST ({SERVER_URL})")
    print("=" * 92)
    print(
        f"runs={args.runs}, warmup={args.warmup}, timeout={args.timeout}s, "
        f"thresholds: text_p95<={args.max_text_p95}s, total_p95<={args.max_total_p95}s"
    )
    print("-" * 92)

    failed: list[str] = []

    for name, payload in scenarios:
        print(f"Scenario: {name}")
        summary, _ = await execute_scenario(
            name=name,
            payload=payload,
            runs=args.runs,
            warmup=args.warmup,
            timeout_s=args.timeout,
            verbose=args.verbose,
        )
        print_summary(summary)

        if summary.p95_text_s > args.max_text_p95:
            failed.append(
                f"{name}: text p95 {summary.p95_text_s:.2f}s > {args.max_text_p95:.2f}s"
            )
        if summary.p95_total_s > args.max_total_p95:
            failed.append(
                f"{name}: total p95 {summary.p95_total_s:.2f}s > {args.max_total_p95:.2f}s"
            )

        print("-" * 92)

    if failed:
        print("❌ Latency regression detected:")
        for item in failed:
            print(f"  - {item}")
        return 1

    print("✅ All latency thresholds satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
