@echo off
setlocal
cd /d "%~dp0"

echo Uploading the updated bot to Beget...
rem VPN settings stay on the server: vpn/config.json contains private connection data.
if "%BEGET_HOST%"=="" (
  echo ERROR: Set BEGET_HOST before running this script, for example:
  echo set BEGET_HOST=your-server.example
  pause
  exit /b 1
)

scp bot.py Dockerfile docker-compose.yml docker-compose.beget.yml requirements.txt root@%BEGET_HOST%:/opt/telegram-ai-bot/
if errorlevel 1 goto :error

echo Rebuilding and restarting the container...
ssh root@%BEGET_HOST% "cd /opt/telegram-ai-bot && docker compose -f docker-compose.yml -f docker-compose.beget.yml up -d --build --force-recreate && docker compose -f docker-compose.yml -f docker-compose.beget.yml ps && docker compose -f docker-compose.yml -f docker-compose.beget.yml logs --tail=30"
if errorlevel 1 goto :error

echo.
echo Done. Test the bot in Telegram.
pause
exit /b 0

:error
echo.
echo Update failed. Check the password and internet connection.
pause
exit /b 1
