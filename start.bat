@echo off
chcp 65001 >nul
echo ====================================
echo   NIKKE PVP Tracker
echo ====================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt -q
echo.

echo [2/3] Starting server...
echo.
echo Open http://localhost:5000 in your browser
echo Press Ctrl+C to stop
echo.

start http://localhost:5000
python app.py

pause
