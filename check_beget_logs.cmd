@echo off
title Bot6 Beget logs
echo Checking the last bot errors on Beget...
echo.
if "%BEGET_HOST%"=="" (
  echo ERROR: Set BEGET_HOST before running this script, for example:
  echo set BEGET_HOST=your-server.example
  pause
  exit /b 1
)

ssh root@%BEGET_HOST% "docker logs telegram-ai-bot --since 20m --tail 150 2>&1"
echo.
echo Send a screenshot of the last error lines to Codex.
pause
