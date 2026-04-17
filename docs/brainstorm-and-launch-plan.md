# MindBotz Brainstorm + Launch Plan

This file is the dedicated home for brainstorming, roadmap, and launch execution notes so `README.md` can stay focused on project setup and running.

## Current priorities

- Deploy and launch quickly.
- Keep setup friction low.
- Preserve privacy-first, on-device positioning.

## Launch-tomorrow checklist

- [ ] Confirm clean install path on macOS/Linux with `uv sync`.
- [ ] Confirm clean install path on Windows with `scripts/start_windows.bat`.
- [ ] Record a short demo clip.
- [ ] Verify README quick-start accuracy.
- [ ] Create release notes for known limitations.

## If GitHub says "unable to merge"

Use this flow on your branch:

```bash
git fetch origin
git checkout <your-branch>
git rebase origin/main
# resolve conflicts in files, then:
git add <resolved-files>
git rebase --continue
# when done:
git push --force-with-lease
```

If you prefer merge instead of rebase:

```bash
git fetch origin
git checkout <your-branch>
git merge origin/main
# resolve conflicts, then:
git add <resolved-files>
git commit
git push
```

## Operator workflow

### Daily setup loop

1. Keep `main` clean.
2. Create a branch per task.
3. Make small commits.
4. Open a PR early.

Example:

```bash
git checkout main
git pull origin main
git checkout -b feat/mindbot-preset-tuning
# hack, test, commit
git push -u origin feat/mindbot-preset-tuning
```

### Branch strategy

- `main`: stable and demo-ready
- `develop`: integration branch for near-term features
- `feat/*`: short-lived feature work
- `fix/*`: bug fixes
- `exp/*`: spikes and prototypes
- `release/*`: optional release hardening branches

### Shipping checklist

Before merge:

- [ ] Feature works end-to-end locally.
- [ ] No secrets in the diff.
- [ ] README or docs updated.
- [ ] Tests or manual validation steps listed.
- [ ] Rollback plan noted in the PR.

Before release:

- [ ] Tag a version.
- [ ] Write release notes.
- [ ] List known issues.
- [ ] Capture a demo clip or screenshot.

## Brainstorm ideas

### Product experience

- Realtime captions mode.
- Avatar or video response mode.
- Multilingual coaching personalities.
- Fast demo mode preset for low-latency live demos.

### Reliability and UX

- Better websocket reconnect handling.
- Persistent chat or session history export.
- Diagnostics panel for latency, VAD state, and model load time.
- Guided first-run health checks for mic, camera, and GPU.

### Distribution

- Optional packaged desktop app wrapper.
- Improved one-command setup for each platform.
- Preflight environment checker script.

## Notes

Use this file as the living brainstorm board. Promote only polished, user-facing content back into `README.md`.
