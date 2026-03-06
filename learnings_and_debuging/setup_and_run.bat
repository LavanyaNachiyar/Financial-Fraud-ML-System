@echo off
echo ========================================
echo One Pass Learning - Setup and Run
echo ========================================

echo.
echo [1/4] Creating virtual environment...
python -m venv venv

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Installing dependencies...
pip install flask flask-sqlalchemy scikit-learn numpy pandas joblib qrcode[pil] flask-socketio

echo.
echo [4/4] Starting Flask application...
echo.
echo ========================================
echo Application will run at http://localhost:5000
echo Press Ctrl+C to stop the server
echo ========================================
echo.
python app.py
