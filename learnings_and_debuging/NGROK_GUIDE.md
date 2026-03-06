# 🌐 Ngrok Integration Guide

## What is Ngrok?
Ngrok creates a secure tunnel to your localhost, making your app accessible from anywhere on the internet. Perfect for testing on real mobile devices!

## Quick Setup

### 1. Install Dependencies
```bash
venv\Scripts\activate
pip install pyngrok
```

### 2. Run with Ngrok
```bash
run_with_ngrok.bat
```

Or manually:
```bash
python app.py
```

### 3. Get Your Public URL
When the app starts, you'll see:
```
============================================================
🌐 NGROK TUNNEL ACTIVE
============================================================
Public URL: https://xxxx-xx-xx-xx-xx.ngrok-free.app
Local URL:  http://localhost:5000
============================================================
```

## Usage

### Share Payment Link
1. Login to dashboard
2. Click "Generate Payment QR"
3. Share the **Public URL** with anyone
4. They can scan QR or open link on their phone
5. You'll receive real-time alerts!

### Test on Real Phone
1. Start app with ngrok
2. Copy the public URL
3. Open on your phone's browser
4. Make a test payment
5. See results on both devices instantly!

## Disable Ngrok (Local Only)

Set environment variable:
```bash
set NGROK_ENABLED=false
python app.py
```

Or edit `app.py`:
```python
NGROK_ENABLED = False
```

## Troubleshooting

### "Ngrok failed" Error
1. Check internet connection
2. Install ngrok: `pip install --upgrade pyngrok`
3. Restart the application

### Tunnel Expired
- Free ngrok tunnels expire after 2 hours
- Just restart the app to get a new URL

### Can't Access from Phone
- Make sure phone is connected to internet (not just WiFi)
- Use the ngrok URL, not localhost
- Check firewall settings

## Features with Ngrok

✅ **Access from anywhere**
- Share link with friends/family
- Test on real mobile devices
- Demo to clients remotely

✅ **Real QR Code Testing**
- Scan with actual phone camera
- Test mobile payment flow
- Verify responsive design

✅ **Live Fraud Detection**
- Real-time alerts across devices
- Test from different locations
- Simulate real-world scenarios

## Security Note

⚠️ **For Development Only**
- Don't use in production
- Don't share sensitive data
- Free ngrok URLs are public

## Example Workflow

1. **Start app**: `run_with_ngrok.bat`
2. **Copy URL**: `https://xxxx.ngrok-free.app`
3. **Login**: Use ngrok URL on desktop
4. **Generate QR**: Click button in dashboard
5. **Scan**: Use phone to scan QR code
6. **Pay**: Fill details and click "Pay Now"
7. **Watch**: See alerts on both screens!

Perfect for demos and testing! 🚀
