# Windows Beta Setup Notes

This branch now supports three setup improvements for local models:

- `src/server.py` loads `.env` from the repo root.
- If `MODEL_PATH` is unset, the server checks `./models/*.litertlm` before trying Hugging Face.
- `scripts/start_windows.bat` auto-detects `models/Gemma-4-E2B-it-abliterated.litertlm` and reports the real install failure reason.

## Your downloaded model

If you keep the model at:

```text
Z:\G1T-UN1V3RS3\parlor\models\Gemma-4-E2B-it-abliterated.litertlm
```

the server now picks it up automatically. You can also pin it explicitly in a repo-root `.env` file:

```dotenv
MODEL_PATH=./models/Gemma-4-E2B-it-abliterated.litertlm
PORT=8000
```

## Native Windows status

As of 2026-04-17, native Windows is still blocked by the LiteRT-LM package itself:

- `uv sync` fails on `win_amd64`
- the missing package is `litert-lm-api==0.10.1`
- upstream currently publishes wheels for macOS ARM64 and Linux, not native Windows

That means the batch file can now validate and wire your model path, but it still cannot complete a full native Windows runtime until LiteRT-LM publishes Windows support.

## Supported way to run this branch with your local model

Use the same repository on a supported platform and point `MODEL_PATH` at the local `.litertlm` file.

### macOS or Linux

```bash
cd src
uv sync
MODEL_PATH=../models/Gemma-4-E2B-it-abliterated.litertlm uv run server.py
```

### WSL example

If your `Z:` drive is mounted in WSL, the equivalent path is typically:

```bash
/mnt/z/G1T-UN1V3RS3/parlor/models/Gemma-4-E2B-it-abliterated.litertlm
```

Then run:

```bash
cd /mnt/z/G1T-UN1V3RS3/parlor/src
uv sync
MODEL_PATH=/mnt/z/G1T-UN1V3RS3/parlor/models/Gemma-4-E2B-it-abliterated.litertlm uv run server.py
```
