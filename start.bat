@echo off
chcp 65001 >nul
title NIKKE PVP Tracker
set PYTHONIOENCODING=utf-8
echo ====================================
echo   NIKKE PVP Tracker
echo ====================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt -q
echo.

echo [2/3] Starting server...

:: 自动打开浏览器（端口跟随 exe 自适应，默认 5000）
start http://localhost:5000

:: 启动 exe
start /B "" "%~dp0nikke-pvp-tracker.exe"

echo [3/3] Server started at http://localhost:5000
echo Close this window to stop the server.
echo.
timeout /t 2 >nul
