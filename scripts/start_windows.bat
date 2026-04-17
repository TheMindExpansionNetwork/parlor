@echo off
setlocal

for %%I in ("%~dp0..") do set "REPO_ROOT=%%~fI"
set "MODEL_CANDIDATE=%REPO_ROOT%\models\Gemma-4-E2B-it-abliterated.litertlm"

if not defined MODEL_PATH (
  if exist "%MODEL_CANDIDATE%" (
    set "MODEL_PATH=%MODEL_CANDIDATE%"
  )
)

cd /d "%REPO_ROOT%\src"
if errorlevel 1 (
  echo Failed to enter src directory.
  exit /b 1
)

echo Repo root: %REPO_ROOT%
if defined MODEL_PATH (
  echo MODEL_PATH=%MODEL_PATH%
) else (
  echo MODEL_PATH is not set. The server will look in the repo models folder first.
)

echo [1/2] Syncing dependencies with uv...
call uv sync
if errorlevel 1 (
  echo uv sync failed.
  echo.
  echo Native Windows is currently blocked by LiteRT-LM packaging.
  echo This beta branch now auto-detects your local .litertlm file, but the runtime still needs macOS or Linux to install litert-lm.
  echo See README.md and docs\windows-beta-setup.md for the supported setup path.
  exit /b 1
)

echo [2/2] Starting server...
call uv run server.py
