@echo off
echo ========================================
echo Starting WITHOUT Ngrok (Local Only)
echo ========================================

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting application...
echo Access at: http://localhost:5000
echo.

set NGROK_ENABLED=false
python app.py

pause
