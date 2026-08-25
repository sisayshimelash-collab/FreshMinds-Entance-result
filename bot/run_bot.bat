@echo off
title FreshMinds EAES Result Bot
echo ===================================================
echo Starting FreshMinds EAES Result Bot...
echo ===================================================
cd /d "%~dp0"

:loop
python main.py
echo.
echo [WARNING] Bot stopped or crashed. Restarting in 5 seconds... (Press Ctrl+C to abort)
timeout /t 5
goto loop
