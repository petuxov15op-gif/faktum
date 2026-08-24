@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" (
  echo ERROR: .env file was not found.
  echo Create .env from .env.example and add your API keys.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: Python environment .venv was not found.
  pause
  exit /b 1
)

echo Starting Telegram bot. Keep this window open.
echo Press Ctrl+C to stop the bot.
".venv\Scripts\python.exe" "bot.py"

echo.
echo Bot stopped.
pause
