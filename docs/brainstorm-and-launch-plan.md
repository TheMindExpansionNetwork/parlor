# MindBotz Brainstorm + Launch Plan

This file is the dedicated home for brainstorming, roadmap, and launch execution notes so `README.md` can stay focused on project setup + running.

## Current priorities (for launch)

- Deploy and launch quickly.
- Keep setup friction low.
- Preserve privacy-first, on-device positioning.

## Launch-tomorrow checklist

- [ ] Confirm clean install path on macOS/Linux with `uv sync`.
- [ ] Confirm clean install path on Windows with `scripts/start_windows.bat`.
- [ ] Record short demo clip.
- [ ] Verify README quick-start accuracy.
- [ ] Create release notes for known limitations.

## If GitHub says "unable to merge" (conflicts)

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

## Notes

Use this file as the living brainstorm board. Promote only polished, user-facing content back into `README.md`.
