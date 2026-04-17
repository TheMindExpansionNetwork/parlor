# MindBotz Brainstorm + Launch Plan

This doc holds the idea dump and execution plan so the main README can stay product-focused.

## Current priorities (for launch)

- Deploy and launch quickly.
- Keep setup friction low.
- Preserve privacy-first, on-device positioning.

## Brainstorm ideas

### Product experience

- Realtime captions mode.
- Avatar/video response mode.
- Multilingual coaching personalities.
- “Fast demo mode” preset for low-latency live demos.

### Reliability + UX

- Better websocket reconnect handling.
- Persistent chat/session history export.
- Diagnostics panel (latency, VAD state, model load time).
- Guided first-run health checks (mic/camera/GPU).

### Distribution

- Optional packaged desktop app wrapper.
- Improved one-command setup for each platform.
- Preflight environment checker script.

## Launch-tomorrow checklist

- [ ] Confirm clean install path on macOS/Linux with `uv sync`.
- [ ] Confirm clean install path on Windows with `scripts/start_windows.bat`.
- [ ] Record short demo clip.
- [ ] Verify README quick-start accuracy.
- [ ] Create release notes for known limitations.

## Branch/PR workflow reminders

- Keep `main` stable.
- Use short-lived branches:
  - `feat/*`
  - `fix/*`
  - `docs/*`
- Keep commits focused and easy to review.

## Notes

Use this file as the living brainstorm board. Promote only polished, user-facing content back into `README.md`.
