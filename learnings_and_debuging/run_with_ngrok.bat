@echo off
echo ========================================
echo Starting Fraud Detection with Ngrok
echo ========================================

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing ngrok (if needed)...
pip install pyngrok

echo.
echo ========================================
echo Starting application with ngrok...
echo ========================================
echo.

python app.py

pause
