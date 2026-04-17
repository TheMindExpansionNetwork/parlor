# LFM2.5 Camera Security + Roast Mode Research Guide

## TL;DR
- `LiquidAI/LFM2.5-350M` is **text-only**. It cannot directly read camera frames.
- For camera vision, use a vision-language model such as `LiquidAI/LFM2.5-VL-450M` (or `LFM2.5-VL-1.6B` if you can afford more compute).
- Best architecture: **camera frame sampler + person detector + VLM captioning + mode state machine + TTS output**.
- You can add a "roast" personality mode, but implement **safety filters** so it stays playful and avoids harassment/hate content.

---

## 1) What the model link you shared is (and is not)

You shared: `https://huggingface.co/LiquidAI/LFM2.5-350M`

From the model card, `LFM2.5-350M` is a general-purpose **text-only** instruct model intended for extraction, structured outputs, and tool use. It is not a multimodal checkpoint that takes image tensors.

### What this means practically
- If your input is a webcam frame, you need either:
  1. A separate vision model (detector/captioner) before the text model, or
  2. A native VLM model (`LFM2.5-VL-*`) that accepts image+text in chat format.

---

## 2) Which Liquid model to use for camera-based behavior

For your use case ("if person enters frame, react and speak") use `LiquidAI/LFM2.5-VL-450M` first:

### Why `LFM2.5-VL-450M`
- Built on LFM2.5-350M backbone + vision encoder.
- Supports image+text prompting with Hugging Face `AutoModelForImageTextToText`.
- Designed for low-latency and edge scenarios.
- Adds bounding box / grounding support and function-calling support (text-side), helpful for event pipelines.

### When to choose `LFM2.5-VL-1.6B` instead
- If you need stronger scene understanding and can handle more latency and memory.
- If you do more than security banter (e.g., detailed analytics, OCR-heavy tasks).

---

## 3) Recommended system architecture

```text
Webcam stream
  -> Frame sampler (e.g., 1-2 FPS for reasoning)
  -> Person detector/tracker (YOLO/RT-DETR/OpenCV DNN)
  -> Event engine (entered frame, lingered, exited)
  -> LFM2.5-VL prompt builder (mode-specific persona)
  -> Response policy filter (safety, profanity, protected classes)
  -> TTS output + subtitle overlay
  -> Alert sink (webhook/SMS/home-automation only in security mode)
```

### Why split detector + VLM
- Detector/tracker is cheap and stable for "person entered" events.
- VLM is used only when needed for richer text.
- This lowers token cost and improves real-time responsiveness.

---

## 4) Mode design (state machine)

Create explicit modes with clear transition logic.

## Modes
1. **Idle**: no person detected.
2. **Investigate**: person detected for N frames; describe scene and intent estimate.
3. **Security**: unknown person or suspicious event; warn + optionally notify.
4. **Hype/Roast Merch Mode**: playful commentary and upsell style lines.

## Suggested transitions
- `Idle -> Investigate`: person confidence > threshold for 1-2 seconds.
- `Investigate -> Security`: unknown face, odd hours, restricted zone, or loitering > X seconds.
- `Investigate -> Roast`: recognized friend/visitor + confidence high + allowed profile flag.
- Any mode -> `Idle`: no person for Y seconds.

Keep a **cooldown** (e.g., 8-12 sec) to prevent repetitive speech spam.

---

## 5) Prompt templates you can use

Use one system prompt per mode, then inject live scene facts from detector + VLM frame summary.

## Security mode system prompt
```text
You are a home security assistant speaking over a smart speaker.
Style: short, direct, assertive. 1 sentence max unless asked.
If a person is visible, challenge politely: "Hey, what are you doing here?"
Never mention protected traits. Avoid threats. Do not escalate beyond warning + notify owner.
If uncertain, say you are uncertain.
```

## Roast/merch mode system prompt (safer version)
```text
You are a playful fashion roast MC for consenting users.
Tone: funny, light, PG-13, no hate speech, no slurs, no harassment.
Roast only clothing/style choices in a cartoonish way.
End every line with a positive merch suggestion (hat/hoodie) and one compliment.
Max 2 short sentences.
```

## User content payload template
```json
{
  "role": "user",
  "content": [
    {"type": "image", "image": "<current_frame>"},
    {"type": "text", "text": "Mode=SECURITY. Facts: person_count=1, zone=living_room, time=23:48, known_face=false. Generate one spoken line."}
  ]
}
```

---

## 6) Minimal Python inference example (Hugging Face)

```python
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText

model_id = "LiquidAI/LFM2.5-VL-450M"

model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)

image = Image.open("frame.jpg").convert("RGB")
conversation = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": "Mode=SECURITY. person_count=1. unknown_face=true. Generate one short warning line."}
        ],
    }
]

inputs = processor.apply_chat_template(
    conversation,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
    tokenize=True,
).to(model.device)

with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=48, temperature=0.6)

text = processor.batch_decode(output, skip_special_tokens=True)[0]
print(text)
```

---

## 7) Real-time pipeline pseudocode

```python
while True:
    frame = camera.read()
    detections = person_detector(frame)

    event = state_machine.update(detections, now=time.time())

    if event.should_speak and cooldown.ready():
        mode = event.mode
        scene_facts = build_scene_facts(detections, metadata)

        vlm_text = generate_line_with_lfm2_vl(frame, mode, scene_facts)
        safe_text = safety_filter(vlm_text, mode)

        tts.speak(safe_text)

    if event.should_alert_owner:
        notify_owner(event.snapshot, event.summary)
```

---

## 8) Guardrails you definitely want

Because you asked for roast behavior, use strict policy checks before speaking:

- Block content referencing protected attributes (race, religion, disability, etc.).
- Block sexual or threatening content.
- Block doxxing/private details.
- Keep tone playful and opt-in only (people in household must consent).
- Add a hard "safe mode" switch phrase: **"Security, be respectful"**.
- Log outputs for review and tuning.

Recommended implementation:
1. Generate candidate line.
2. Run moderation rules/classifier.
3. If blocked, replace with safe fallback ("Welcome in—check out the hat drop!").

---

## 9) Practical defaults for your first build

- Frame sampling: 1 FPS for VLM, 8-15 FPS for lightweight detector.
- Trigger threshold: person detected continuously for 1.2s.
- Speech cooldown: 10s.
- Max utterance length: 18 words.
- Security mode confidence threshold stricter than roast mode.
- Keep a per-person memory key for 30-60s to avoid repeating same line.

---

## 10) Suggested launch plan

1. Start with **Security mode only** (neutral voice).
2. Add alert webhook (phone/home assistant) and event logs.
3. Add Roast mode behind explicit toggle and consent list.
4. A/B test prompt variants for shortness + fun factor.
5. Add merch tool-call (e.g., returns product URL) only after behavior is stable.

---

## 11) Source links

- LFM2.5-350M model card: https://huggingface.co/LiquidAI/LFM2.5-350M
- LFM2.5-VL-450M model card: https://huggingface.co/LiquidAI/LFM2.5-VL-450M
- Transformers LFM2-VL docs: https://huggingface.co/docs/transformers/en/model_doc/lfm2_vl

