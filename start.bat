@echo off
chcp 65001 >nul
title NIKKE PVP Tracker
set PYTHONIOENCODING=utf-8
echo ====================================
echo   NIKKE PVP Tracker
echo ====================================
echo.
echo [1/2] Launching server...
start http://localhost:5000
start /B "" "%~dp0nikke-pvp-tracker.exe"
echo Server started at http://localhost:5000
echo Close this window to stop the server.
echo.
timeout /t 3 >nul
