@echo off
echo ========================================
echo Ngrok Setup
echo ========================================
echo.
echo Step 1: Sign up for ngrok (if you haven't)
echo Visit: https://dashboard.ngrok.com/signup
echo.
echo Step 2: Get your authtoken
echo Visit: https://dashboard.ngrok.com/get-started/your-authtoken
echo.
echo Step 3: Enter your authtoken below
echo.
set TOKEN=3AYkZf9mwDM0f3YBmdulqH8MNLy_5hr11dCwdBH3WpMudgkKr

echo.
echo Setting up ngrok...
ngrok config add-authtoken %TOKEN%

echo.
echo ========================================
echo Setup Complete!
echo Now run: python app.py
echo ========================================
pause
