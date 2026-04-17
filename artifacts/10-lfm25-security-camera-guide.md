# LFM2.5 Camera Security + “Roast Mode” Build Guide (Updated April 17, 2026)

## Quick answer to your link
You shared `LiquidAI/LFM2.5-350M`.

- That exact model is **text-only**.
- For live camera behavior, use a **vision-language model** from the same family:
  - `LiquidAI/LFM2.5-VL-450M` (fastest/smallest)
  - `LiquidAI/LFM2.5-VL-1.6B` (stronger visual reasoning, higher compute)

So: keep `LFM2.5-350M` for text logic if you want, but for camera frames you should run `LFM2.5-VL-*`.

---

## What to run for your use case
Your goals:
1. Detect person enters room
2. Stay in “investigation/security” behavior
3. Speak in character ("hey what you doing here")
4. Optional playful roast + merch upsell mode

### Recommended model choice
Start with **`LFM2.5-VL-450M`** for real-time edge speed.

Why:
- It is the LFM2.5 vision-language variant (image+text input).
- Built on LFM2.5-350M backbone with a vision encoder.
- Designed for low-latency use and local deployment options (native / GGUF / ONNX).

Use **`LFM2.5-VL-1.6B`** only if you need better OCR/multi-image detail and can tolerate extra latency.

---

## Architecture that works in production

```text
Camera stream (15-30 FPS)
  -> lightweight person detector/tracker (8-15 FPS)
  -> event engine (entered, lingered, exited, restricted-zone)
  -> frame sampler for VLM (1-2 FPS only when needed)
  -> LFM2.5-VL prompt by mode
  -> safety/policy filter
  -> TTS output + optional webhook alert
```

### Why split detector + VLM
- Detector handles real-time motion/person events cheaply.
- VLM is called only when you need language (“what should I say now?”).
- This gives much better latency and less repeated speech spam.

---

## State machine (important)

### Modes
- **IDLE**: no person
- **INVESTIGATE**: person entered; gather context
- **SECURITY**: unknown person / odd hours / restricted zone
- **ROAST_MERCH**: playful line + merch suggestion (opt-in only)

### Suggested transitions
- `IDLE -> INVESTIGATE`: person seen for >= 1.0s
- `INVESTIGATE -> SECURITY`: unknown_face=true OR zone=restricted OR linger>20s at night
- `INVESTIGATE -> ROAST_MERCH`: known/consenting user + non-security context
- `* -> IDLE`: no person for >= 4s

### Cooldown
Use 8–12 second speech cooldown so it doesn’t repeat every frame.

---

## Prompt packs you can drop in now

## 1) SECURITY mode system prompt
```text
You are a security voice assistant on a home camera.
Style: short, direct, confident. Max 1 sentence.
If person is visible and unknown, challenge politely.
Do not mention protected traits, do not threaten, do not insult.
If uncertain, say you are uncertain.
```

### SECURITY user payload template
```text
Mode=SECURITY
Facts:
- person_count={person_count}
- known_face={known_face}
- zone={zone}
- local_time={local_time}
Generate one spoken line now.
```

### SECURITY sample lines
- “Hey, I don’t recognize you. What are you doing here?”
- “You’re in a monitored area. Please identify yourself.”
- “Heads up: I’m notifying the owner to check this room.”

## 2) INVESTIGATE mode system prompt
```text
You are an investigation assistant.
Goal: ask a calm clarifying question.
Keep it friendly and short. Max 1 sentence.
```

### INVESTIGATE sample lines
- “Hey there, can I help you find someone?”
- “Quick check—are you expected in this room right now?”

## 3) ROAST_MERCH mode system prompt (safer)
```text
You are a playful fashion commentator for consenting users.
Tone: light, funny, PG-13. Max 2 short sentences.
Roast only outfit style in a cartoonish way.
Never target protected traits, body shape, or sensitive attributes.
Always end with one positive compliment and one merch suggestion.
```

### ROAST_MERCH sample lines
- “That outfit looks like it lost a bet—but your confidence is elite. Wanna upgrade with the midnight cap?”
- “You dressed like Monday morning chaos, and somehow it works. Respect. Grab the signature hat and complete the look.”

---

## Minimal Hugging Face inference example (Python)

```python
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText

model_id = "LiquidAI/LFM2.5-VL-450M"

model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)

frame = Image.open("frame.jpg").convert("RGB")
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": frame},
            {"type": "text", "text": "Mode=SECURITY. known_face=false. Generate one spoken line."},
        ],
    }
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
    tokenize=True,
).to(model.device)

with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=48, temperature=0.6)

reply = processor.batch_decode(out, skip_special_tokens=True)[0]
print(reply)
```

---

## Real-time controller pseudocode

```python
while True:
    frame = cam.read()
    dets = detector.track(frame)

    event = state_machine.update(dets, now=time.time())

    if event.should_speak and cooldown.ready():
        mode = event.mode
        prompt = build_prompt(mode, event.facts)
        line = vlm_generate(frame, prompt)
        line = policy_filter(line, mode)
        tts.speak(line)

    if event.should_alert:
        send_alert(snapshot=frame, summary=event.summary)
```

---

## Safety + legal guardrails (US practical)

1. **Consent for roast mode**: make this opt-in per known user.
2. **Default unknown users to SECURITY tone**, not insults.
3. **No protected-class targeting** (race, religion, disability, etc.).
4. **Two-party consent states** can restrict audio recording; check local law before storing voice.
5. Add a global safe phrase (example): **“Security, respectful mode.”**
6. Store logs for review; keep retention short.

---

## Tuning defaults for first stable version
- Person detector: 10 FPS
- VLM call rate: 1 FPS (event-triggered)
- Enter threshold: 1.0s continuous detection
- Linger threshold: 20s
- Speech cooldown: 10s
- Max words spoken: 18
- Fallback line when policy blocks output:
  - “Welcome in. If you need help, say hello.”

---

## “Tell surf” style line pack (your vibe)
If you want that playful “I’m going to tell…” behavior:

- “Heyy, what you doing here? I’m about to report this to the boss cam.”
- “I see you in frame—don’t act innocent, I’m logging this entrance.”
- “Friendly warning: this room has receipts, and I keep all of them.”

Use these in **SECURITY** or **INVESTIGATE** with moderation filters.

---

## Sources
- LFM2.5-350M model card (text-only description): https://huggingface.co/LiquidAI/LFM2.5-350M
- LFM2.5-VL-450M model card (vision-language details): https://huggingface.co/LiquidAI/LFM2.5-VL-450M
- LFM2.5-VL-1.6B model card (larger VL variant): https://huggingface.co/LiquidAI/LFM2.5-VL-1.6B
- Liquid docs (LFM2.5-VL-450M page): https://docs.liquid.ai/lfm/models/lfm25-vl-450m
- Hugging Face Transformers LFM2-VL docs (API/classes/examples): https://huggingface.co/docs/transformers/en/model_doc/lfm2_vl
