@echo off
setlocal

cd /d "%~dp0..\\src"
if errorlevel 1 (
  echo Failed to enter src directory.
  exit /b 1
)

echo [1/2] Syncing dependencies with uv...
call uv sync
if errorlevel 1 (
  echo uv sync failed.
  exit /b 1
)

echo [2/2] Starting server...
call uv run server.py
