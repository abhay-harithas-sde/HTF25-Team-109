@echo off
echo 🍽️ FoodVision AI - Starting Application
echo =====================================

echo.
echo 🐍 Starting Backend Server...
start "FoodVision Backend" cmd /k "cd /d %~dp0 && venv\Scripts\python.exe backend\app_simple.py"

echo.
echo ⚛️ Starting Frontend Server...
timeout /t 3 /nobreak >nul
start "FoodVision Frontend" cmd /k "cd /d %~dp0\frontend && npm start"

echo.
echo 🌐 Application will be available at:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:5000
echo.
echo 📋 Both servers are starting in separate windows...
echo    Close those windows to stop the servers.
echo.
pause