# Deploy to Render - Step by Step Guide

## Prerequisites
- GitHub account
- Render account (free): https://render.com

## Step 1: Prepare Your Project

1. **Train the model locally first:**
   ```bash
   jupyter notebook onepass.ipynb
   # Run all cells to generate .pkl files
   ```

2. **Commit .pkl files temporarily** (normally ignored):
   - Remove `*.pkl` from `.gitignore` temporarily
   - Or upload them manually to Render later

## Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fraud-detection.git
git push -u origin main
```

## Step 3: Deploy on Render

### 3.1 Create New Web Service
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

### 3.2 Configure Service

**Basic Settings:**
- **Name:** `fraud-detection-app`
- **Region:** Choose closest to you
- **Branch:** `main`
- **Root Directory:** Leave empty
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** 
  ```bash
  pip install -r req.txt
  ```
- **Start Command:**
  ```bash
  gunicorn app:app
  ```

### 3.3 Environment Variables (Optional)
- `NGROK_ENABLED` = `false` (already default)
- `SECRET_KEY` = `your-secret-key-here`

### 3.4 Instance Type
- Select **Free** tier

### 3.5 Deploy
- Click **"Create Web Service"**
- Wait 5-10 minutes for deployment

## Step 4: Access Your App

Your app will be live at:
```
https://fraud-detection-app.onrender.com
```

## Important Notes

⚠️ **Free Tier Limitations:**
- App sleeps after 15 min of inactivity
- First request after sleep takes ~30 seconds
- 750 hours/month free

⚠️ **Database:**
- SQLite works but data resets on redeploy
- For persistent data, upgrade to PostgreSQL

⚠️ **Model Files:**
- Ensure .pkl files are in repo or upload manually
- Alternative: Train model on first startup (slower)

## Troubleshooting

**Build fails?**
- Check `req.txt` has all dependencies
- Verify Python version in `runtime.txt`

**App crashes?**
- Check Render logs
- Ensure .pkl files exist
- Verify gunicorn is in `req.txt`

**Database errors?**
- SQLite may have permission issues
- Consider PostgreSQL for production

## Alternative: Auto-train on Startup

If you don't want to commit .pkl files, modify `app.py`:

```python
import os

if not os.path.exists('online_sgd_model.pkl'):
    print("Training model...")
    # Add training code here
    exec(open('train_model.py').read())

model = joblib.load("online_sgd_model.pkl")
```

## Monitoring

- View logs: Render Dashboard → Your Service → Logs
- Monitor metrics: Dashboard → Metrics tab
- Set up alerts: Dashboard → Settings → Notifications
