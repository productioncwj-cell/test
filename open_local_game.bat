@echo off
cd /d "%~dp0"
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%p /F >nul 2>nul
start "" python server.py
timeout /t 2 >nul
start "" http://127.0.0.1:8000
