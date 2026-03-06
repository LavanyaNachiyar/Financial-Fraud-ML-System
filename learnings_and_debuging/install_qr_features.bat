@echo off
echo ========================================
echo Installing QR Payment Features
echo ========================================

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing new dependencies...
pip install qrcode[pil] flask-socketio

echo.
echo ========================================
echo Installation Complete!
echo.
echo Run: python app.py
echo Then visit: http://localhost:5000
echo ========================================
pause
