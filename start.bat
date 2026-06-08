@echo off
chcp 65001 >nul
title NIKKE PVP Tracker
echo ====================================
echo   NIKKE PVP Tracker
echo ====================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt -q
echo.

echo [2/3] Starting server...

:: 自动打开浏览器
start http://localhost:5000

:: 无控制台模式启动（pythonw），无 pythonw 时回退 python
where pythonw >nul 2>nul
if %errorlevel% equ 0 (
    start /B pythonw app.py
) else (
    start /B python app.py
)

echo [3/3] Server started at http://localhost:5000
echo Close this window to stop the server
echo.
timeout /t 2 >nul
