@echo off
echo ========================================
echo Setting Up Model Performance Metrics
echo ========================================

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing visualization libraries...
pip install matplotlib seaborn

echo.
echo Evaluating model performance...
python evaluate_model.py

echo.
echo ========================================
echo Setup Complete!
echo.
echo New Features Available:
echo   - Model Performance Dashboard
echo   - Confusion Matrix Visualization
echo   - ROC Curve Analysis
echo   - Feature Importance Chart
echo.
echo Access at: http://localhost:5000/model-performance
echo.
echo Starting application...
echo ========================================
echo.

python app.py

pause
