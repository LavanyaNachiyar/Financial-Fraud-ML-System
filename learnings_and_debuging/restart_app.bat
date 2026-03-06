@echo off
echo ========================================
echo Stopping Ngrok and Restarting App
echo ========================================

echo.
echo Killing existing ngrok processes...
taskkill /F /IM ngrok.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting application with fresh ngrok tunnel...
python app.py

pause
