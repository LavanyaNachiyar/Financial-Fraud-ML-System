@echo off
echo ========================================
echo Setting Up Transaction History Feature
echo ========================================

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running database migration...
python migrate_db.py

echo.
echo ========================================
echo Setup Complete!
echo.
echo New Features Available:
echo   - Analytics Dashboard
echo   - Transaction History
echo   - CSV Export
echo.
echo Starting application...
echo ========================================
echo.

python app.py

pause
