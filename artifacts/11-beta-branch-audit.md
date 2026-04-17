# Beta Branch Audit and Consolidation (2026-04-17)

This document records a quick branch and content consolidation pass before creating a `beta` branch.

## Branch Review

Commands used:

```bash
git branch -a
git log --oneline --decorate --graph --all --max-count=20
```

Result: only one active local branch (`work`) existed during this audit, so all available repository features and documentation were already consolidated in a single branch.

## Feature Inventory Included in Beta

- FastAPI + WebSocket realtime server (`src/server.py`)
- Cross-platform TTS layer (`src/tts.py`)
- Browser UI with mic/camera interaction (`src/index.html`)
- Benchmark tooling (`src/benchmarks/*`)

## Documentation Inventory Included in Beta

- Main project documentation (`README.md`)
- Upgrade notes (`AGENT_NOTES_MindBotz_Upgrades.md`)
- Research and planning docs (`artifacts/01` through `artifacts/10`)

## Beta Branch Creation Policy

`beta` should be created directly from the latest audited commit on `work` so the branch includes all currently tracked features and documents.
