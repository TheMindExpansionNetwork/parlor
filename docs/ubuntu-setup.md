# Ubuntu Beta Setup

This branch is intended to be launched from Ubuntu. If you were trying to run it from native Windows, stop there and switch to Ubuntu first.

## Recommended environment

- Ubuntu 24.04 LTS
- Python 3.12
- `curl` and `git`
- A Linux GPU environment that can run `litert-lm`

## 1. Clone the repo

```bash
git clone https://github.com/fikrikarim/parlor.git
cd parlor
git checkout beta
```

## 2. Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
```

If `uv` is already installed, you can skip this step.

## 3. Put your model in `models/` (optional but recommended)

If you already downloaded a `.litertlm` model, place it in the repo `models/` folder.

Example:

```text
parlor/models/Gemma-4-E2B-it-abliterated.litertlm
```

The server automatically checks `models/*.litertlm` before attempting a Hugging Face download.

## 4. Optional config

Create a repo-root `.env` file if you want to pin a model or port:

```dotenv
MODEL_PATH=./models/Gemma-4-E2B-it-abliterated.litertlm
PORT=8000
```

## 5. Launch

Use the Ubuntu launcher:

```bash
./scripts/start_ubuntu.sh
```

That script:

- resolves the repo root
- auto-detects `models/Gemma-4-E2B-it-abliterated.litertlm` when `MODEL_PATH` is unset
- runs `uv sync`
- starts the FastAPI server with `uv run server.py`

## 6. Open the app

Open:

```text
http://localhost:8000
```

Allow microphone and camera access in the browser, then start talking.

## Manual launch commands

If you do not want to use the helper script:

```bash
cd src
uv sync
MODEL_PATH=../models/Gemma-4-E2B-it-abliterated.litertlm uv run server.py
```

## Troubleshooting

If `uv` is not found:

```bash
source "$HOME/.local/bin/env"
```

If `MODEL_PATH` points to a missing file, the server exits early with the resolved path so you can correct it.

If `litert-lm` fails to install, verify you are actually inside Ubuntu and not native Windows. This branch no longer documents or supports the Windows launcher path.
