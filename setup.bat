@echo off
echo Setting up Law Game environment...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Initialize database
echo Initializing database...
python init_db.py

echo.
echo Setup complete!
echo.
echo To run the application:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run the app: python app.py
echo   3. Open browser to: http://127.0.0.1:5000
echo.
pause