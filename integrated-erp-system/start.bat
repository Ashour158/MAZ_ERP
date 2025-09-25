@echo off
echo 🎬 Integrated ERP System - Complete Working System
echo ================================================
echo Starting the full ERP system with all features...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install requirements
echo 📦 Installing required packages...
python -m pip install flask flask-cors flask-socketio redis PyJWT pandas numpy scikit-learn textblob nltk

echo.
echo 🚀 Starting Integrated ERP System...
echo.

REM Run the system
python run-system.py

echo.
echo 🛑 System stopped
pause
