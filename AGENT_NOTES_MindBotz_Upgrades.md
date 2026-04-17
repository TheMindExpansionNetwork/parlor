# Agent Notes — MindBotz Upgrades (Speed + Personality Switching)

These notes are a practical implementation plan for making the fork feel **faster**, **more fun**, and easier to **switch personalities** safely.

---

## 1) Fastest wins (low risk, high impact)

### A. Add server-side latency telemetry per stage
**Why:** You can’t optimize what you don’t measure.

Track and emit in every response:
- `vad_ms` (speech end → payload send)
- `upload_bytes` (audio/image payload size)
- `llm_ms`
- `tts_ms`
- `first_audio_chunk_ms` (time to first chunk)
- `end_to_end_ms`

**Implementation spot:** `src/index.html` + `src/server.py` websocket messages.

### B. Dynamic image cadence
**Why:** Sending an image every utterance is expensive.

Policy:
- Send image every `N=3` turns by default.
- Always send image if user says trigger phrases (“look”, “see this”, “what is this”).
- In `fast` preset, only send image on explicit visual triggers.

**Expected result:** 20–45% lower payload bandwidth in typical chats.

### C. Tighter response cap by preset
In `fast` preset, force 1 sentence unless user asks “explain more”.

**Implementation:** Add a strict output rule in backend prompt assembly.

### D. Cache frequent TTS snippets
Cache short repeated phrases (`<= 80 chars`) with an LRU map keyed by normalized text.

**Expected result:** Near-zero TTS time for repeated UI-style responses.

---

## 2) Personality system that won’t drift

### A. Move personalities to structured config
Create `src/personas.json`:

```json
{
  "balanced": {
    "label": "Balanced",
    "style": "Clear, concise, neutral.",
    "response_rules": ["1-3 short sentences", "No fluff"]
  },
  "coach": {
    "label": "Coach",
    "style": "Encouraging and corrective when useful.",
    "response_rules": ["Gently fix mistakes", "Give one micro-tip"]
  },
  "fun": {
    "label": "Fun",
    "style": "Playful but still useful.",
    "response_rules": ["Keep concise", "Optional light humor"]
  },
  "fast": {
    "label": "Fast",
    "style": "Ultra-brief and direct.",
    "response_rules": ["One sentence default", "Skip examples unless asked"]
  }
}
```

Then load this in server startup and validate incoming preset names against this set.

### B. Add **modes** separate from personality
Personality = tone. Mode = task behavior.

Recommended modes:
- `chat`
- `language_practice`
- `describe_camera`
- `qa`

Compose prompt as:
`SYSTEM + MODE RULES + PERSONALITY RULES + USER STYLE CHIPS`

This avoids prompt bloat and makes behavior consistent.

### C. Add “stickiness” toggle
- **Sticky off**: preset applies per turn only.
- **Sticky on**: preset persists for session until changed.

Store in frontend state and include in websocket metadata.

---

## 3) Throughput and quality upgrades

### A. Parallelize sentence TTS generation
Current sentence-level streaming can still queue serially.

Better approach:
1. Start generating sentence 1 immediately.
2. Spawn sentence 2 generation while sentence 1 is being encoded/sent.
3. Keep ordered delivery by index.

### B. Smarter sentence splitter
Replace simple regex splitter with abbreviation-aware splitter to avoid tiny sentence fragments.

### C. Adaptive VAD thresholds
Adjust thresholds based on ambient noise floor every 10 seconds.

### D. Optional “audio-only turbo” mode
If camera is disabled or fast preset active, skip image path entirely and use an audio-optimized instruction.

---

## 4) Suggested UX improvements for personality switching

- Show current preset next to status pill: `CONNECTED · COACH`.
- Add keyboard shortcuts:
  - `1` Balanced
  - `2` Coach
  - `3` Fun
  - `4` Fast
- Add “Random mood” button for fun demos.
- Add a tiny preview line under selector: “Coach: encouraging + corrections”.

---

## 5) Safety + reliability guardrails

- Sanitize style-chip/freeform style input length (max 200 chars).
- Allowlist preset keys; fallback to `balanced`.
- Add timeout around LLM call; return graceful apology + retry hint.
- Add queue backpressure if websocket receives turn while processing.

---

## 6) Minimal phased rollout plan

### Phase 1 (1 day)
- Telemetry fields
- Dynamic image cadence
- Strict fast-response cap

### Phase 2 (1–2 days)
- `personas.json` loading + validation
- Mode layer
- Sticky preset toggle

### Phase 3 (2 days)
- TTS cache
- Parallel sentence generation
- Adaptive VAD

---

## 7) Definition of done (measurable)

Target metrics on Apple M3 Pro:
- p50 end-to-end latency: **< 2.2s** (from ~2.5–3.0s baseline)
- Time to first audio chunk: **< 900ms** after LLM done
- Avg payload size reduction in fast mode: **>= 30%**
- Personality correctness (manual eval): **>= 90%** turns match selected preset

---

## 8) Next concrete code tasks

1. Add `src/personas.json` and loader in `src/server.py`.
2. Add `turn_index`, `send_image`, `preset`, `mode`, `sticky` to websocket payload.
3. Implement dynamic image policy in `src/index.html`.
4. Add TTS LRU cache in `src/tts.py` wrapper layer.
5. Emit telemetry to UI transcript meta line for each assistant message.
