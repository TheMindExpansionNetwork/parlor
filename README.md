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
- macOS (Apple Silicon) or Linux with supported GPU
- ~3 GB RAM available for model runtime

---

## Quick start

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

On Windows, you can use `scripts/start_windows.bat` to run `uv sync` and start the server from the repo root.

---


## System latency test

Run a repeatable end-to-end latency gate against the live WebSocket server:

```bash
cd src
uv run python server.py
# in a second terminal
uv run python benchmarks/latency_system_test.py --runs 5 --warmup 1
```

By default the test fails if p95 latency exceeds configured thresholds. Tune limits with `--max-text-p95` and `--max-total-p95`.

## What this fork adds

- **MindBotz rebrand**
- **Conversation presets**: `Balanced`, `Coach`, `Fun`, `Fast`
- **Quick style chips**: `Simple`, `Challenge`, `Emoji`
- **Fast mode optimization**: smaller camera frames + lower JPEG quality for lower latency

Models auto-download on first run (~2.6 GB for Gemma 4 E2B + TTS files).

## Extra project docs

- `docs/brainstorm-and-launch-plan.md` keeps roadmap and launch planning notes out of the main README.
- `scripts/start_windows.bat` gives you a simple Windows bootstrap command for local testing.

---

## MindBot Operator Manual (Codex + iPhone Workflow)

If you want to comfortably build/fork/ship without chaos, use this.

### 1) Daily setup loop (safe + repeatable)

1. **Keep `main` clean**
   - Never do active development on `main`.
2. **Create a branch per task**
   - Name pattern: `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`.
3. **Small commits, often**
   - One intent per commit. Easier review, easier rollback.
4. **Open PR early**
   - Use draft PRs to track decisions and TODOs.

Example:

```bash
git checkout main
git pull origin main
git checkout -b feat/mindbot-preset-tuning
# hack, test, commit
git push -u origin feat/mindbot-preset-tuning
```

### 2) Codex workflow from iPhone (practical path)

Best mobile flow:

1. Use iPhone for **planning + direction**
   - Give Codex scoped tasks: “update README section X,” “add feature flag Y,” “write tests for Z.”
2. Ask Codex to produce:
   - Changes
   - Test commands run
   - Commit
   - PR title/body
3. Review diffs on GitHub mobile app before merge.
4. Merge to `main` only when CI is green.

Prompt template you can reuse:

```text
Work in a new branch named feat/<name>.
Make only the requested change.
Run tests.
Commit with a clear message.
Open a PR with summary + risk notes.
```

### 3) Best branch strategy for shipping

For solo/small-team projects, this is the sweet spot:

- `main`: always releasable
- short-lived feature branches
- optional `release/*` branch only when preparing larger launches

Rules:

- Squash merge PRs to keep history clean
- Require at least one review (or self-review checklist)
- Tag releases: `v0.1.0`, `v0.2.0`, etc.

### 4) Shipping without giving away private/proprietary code

Important truth: if a repo is public, its code is visible. To protect your edge:

- Keep sensitive IP in **private repos/submodules/services**
- Never commit secrets (API keys, certs, private prompts)
- Use `.env` + secret manager
- Add secret scanning + push protection
- Keep production prompts/model tuning assets private when needed
- If open-source, choose a license that matches your intent (Apache/MIT/AGPL/Commercial dual-license)

Quick guardrails:

```bash
# before pushing
git status
git diff --staged
```

And in `.gitignore`, block:

- `.env*`
- credentials, keys, model checkpoints you don’t want distributed
- local cache/artifact folders

### 5) “Comfortable shipping” checklist

Before merge:

- [ ] Feature works end-to-end locally
- [ ] No secrets in diff
- [ ] README/docs updated
- [ ] Tests or manual validation steps listed
- [ ] Rollback plan noted in PR

Before release:

- [ ] Tag version
- [ ] Changelog entry
- [ ] Known issues section
- [ ] Demo clip or screenshot for users

### 6) Session recovery + merge-to-main checklist

If work happened across multiple Codex sessions, run this sequence before you call it done:

```bash
# 1) inspect all local branches
git branch

# 2) compare branch tips against main
git log --oneline --decorate --graph --all --max-count=30

# 3) switch to main and sync (if origin exists)
git checkout main
git pull origin main || true

# 4) merge each completed work branch
git merge <branch-name>

# 5) push updated main
git push origin main
```

Fast sanity check after merge:

```bash
git status
git branch --merged
```

If `main` does not exist yet in your local clone, create it from your current stable branch once:

```bash
git checkout -b main
git push -u origin main
```

---

## Fork + Branch Organization (Game Plan)

If you want to move fast without breaking your production momentum, run a **two-fork setup**:

1. **`upstream/parlor`**
   - Tracks the original project.
   - Pull from here to keep current with upstream improvements.
2. **`your-org/parlor` (your main fork)**
   - Where your product roadmap lives.
   - Protect `main`, merge only via PR.
3. **`your-org/parlor-labs` (optional experimentation fork)**
   - For risky ideas (video pipelines, avatar rendering, model swaps).
   - Cherry-pick successful experiments back into `your-org/parlor`.

### Suggested branch map

- `main` → stable and demo-ready
- `develop` → integration branch for near-term features
- `feat/*` → feature work (short-lived)
- `fix/*` → bug fixes
- `exp/*` → spikes/prototypes (allowed to be messy)
- `release/*` → optional release hardening branches

Branch naming examples:

- `feat/realtime-captions`
- `feat/video-avatar-streaming`
- `fix/websocket-reconnect`
- `exp/rtc-vs-websocket-audio`

---

## Future Features Backlog (Voice Agent + Video)

### Priority 1: Voice-agent reliability (build this first)

- Robust reconnect handling (network drops, tab sleep)
- Better interruption behavior (barge-in while TTS speaks)
- Streaming partial transcript + “thinking” states in UI
- Session memory controls (`short`, `balanced`, `deep`)
- Prompt safety rails and moderation hooks

### Priority 2: Better UX for daily usage

- Push-to-talk + hands-free modes
- Saved personas / presets per use case (coach, tutor, sales, support)
- Conversation export (txt/json/audio transcript bundle)
- Latency/performance panel in UI
- Multi-device profile sync (optional, can be local-first)

### Priority 3: Video-native capabilities

- Live video understanding mode (continuous frame summarization)
- Screen-share understanding (desktop/web tab)
- Optional avatar output (talking head / animated reaction)
- Clip capture + share snippets
- Multi-camera selection and quality presets

### Priority 4: “Pro” platform features

- Plug-in/tool calling (calendar, CRM, docs, task tools)
- Team workspaces + role-based settings
- Usage metering (tokens/seconds/latency) per session
- Local vs cloud model routing policy engine
- Billing/invoicing hooks (if you commercialize)

---

## 30-60-90 Day Execution Plan

### Next 30 days (stability + trust)

- Lock down branch protections and PR templates
- Ship reconnect + barge-in polish
- Add minimal telemetry (latency, drop rate, failure rate)
- Produce one polished end-to-end demo workflow

### Day 31-60 (product stickiness)

- Release persona presets + conversation export
- Add session memory controls
- Launch a small private beta group with weekly feedback

### Day 61-90 (video differentiation)

- Release first “video understanding mode”
- Add clip capture and a social/demo-ready output flow
- Evaluate avatar pipeline feasibility in `exp/*` branches

---

## Tomorrow’s Focus (High ROI)

If you’re investing tomorrow and want maximum signal fast, do this order:

1. **Stability sprint (half day)**
   Tighten reconnect, interruption, and error states.
2. **One wow feature (half day)**
   Ship realtime captions + transcript export.
3. **Ship loop setup (1-2 hours)**
   PR template, issue labels, and branch conventions.
4. **Distribution prep (1-2 hours)**
   Record a short demo clip showing voice + camera + low latency.

This sequence improves retention and demo quality immediately, while keeping the codebase organized for bigger bets (video agents, avatars, tool calling).

---

## Configuration

| Variable     | Default                        | Description                                    |
| ------------ | ------------------------------ | ---------------------------------------------- |
| `MODEL_PATH` | auto-download from HuggingFace | Path to a local `gemma-4-E2B-it.litertlm` file |
| `PORT`       | `8000`                         | Server port                                    |

---

## Performance (Apple M3 Pro)

| Stage                            | Time          |
| -------------------------------- | ------------- |
| Speech + vision understanding    | ~1.8-2.2s     |
| Response generation (~25 tokens) | ~0.3s         |
| Text-to-speech (1-3 sentences)   | ~0.3-0.7s     |
| **Total end-to-end**             | **~2.5-3.0s** |

Decode speed: ~83 tokens/sec on GPU (Apple M3 Pro).

---

## Project structure

```text
src/
├── server.py              # FastAPI WebSocket server + Gemma 4 inference
├── tts.py                 # Platform-aware TTS (MLX on Mac, ONNX on Linux)
├── index.html             # Frontend UI (VAD, camera, audio playback)
├── pyproject.toml         # Dependencies
└── benchmarks/
    ├── bench.py           # End-to-end WebSocket benchmark
    └── benchmark_tts.py   # TTS backend comparison
```

---

## Acknowledgments

- [Gemma 4](https://ai.google.dev/gemma) by Google DeepMind
- [LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM) by Google AI Edge
- [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) by Hexgrad
- [Silero VAD](https://github.com/snakers4/silero-vad) for voice activity detection

## License

[Apache 2.0](LICENSE)
