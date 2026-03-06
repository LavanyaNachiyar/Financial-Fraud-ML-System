# 🚀 Real-Time QR Code Payment Simulation - Setup Guide

## New Features Added

### 1. **QR Code Payment Gateway** 🔒
- Generate QR codes for payment simulation
- Real-time fraud detection during payment
- GPay-style mobile payment interface

### 2. **Real-Time Notifications** 📡
- WebSocket-based live updates
- Backend dashboard receives instant alerts
- Simultaneous fraud detection on both ends

### 3. **Mobile-Optimized Payment Page** 📱
- Responsive design like GPay/PhonePe
- User-friendly transaction form
- Instant fraud probability display

## Installation Steps

### 1. Install New Dependencies
```bash
# Activate virtual environment
venv\Scripts\activate

# Install new packages
pip install qrcode[pil] flask-socketio
```

### 2. Retrain Model (if needed)
```bash
python retrain_model.py
```

### 3. Run the Application
```bash
python app.py
```

## How to Use

### For Backend User (Admin/Merchant):

1. **Login** to the dashboard at `http://localhost:5000`

2. **Generate QR Code**:
   - Click "Generate Payment QR" button
   - QR code will be displayed
   - Keep this page open to receive real-time alerts

3. **Monitor Transactions**:
   - When someone scans and pays, you'll see instant notification
   - Shows fraud probability and transaction status

### For Mobile User (Customer):

1. **Scan QR Code** using phone camera or QR scanner

2. **Payment Page Opens**:
   - Enter transaction amount
   - Fill transaction details
   - Click "Pay Now"

3. **Instant Result**:
   - ✅ Green = Payment Approved (Low fraud risk)
   - 🚨 Red = Payment Blocked (High fraud risk)

## Testing the System

### Test Case 1: Normal Transaction
```
Amount: 2000
Type: Credit Card (0)
Time: 14 (2 PM)
Balance: 50000
Merchant Risk: 0.2
```
**Expected**: ✅ Payment Successful

### Test Case 2: Fraudulent Transaction
```
Amount: 18000
Type: Debit Card (1)
Time: 2 (2 AM)
Balance: 5000
Merchant Risk: 0.9
```
**Expected**: 🚨 Transaction Blocked

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Backend User   │         │   Mobile User    │
│  (Dashboard)    │         │  (Payment Page)  │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │  1. Generate QR           │
         │◄──────────────────────────┤
         │                           │
         │                    2. Scan QR
         │                           │
         │                    3. Fill Details
         │                           │
         │  4. Real-time Alert       │ 4. Fraud Check
         │◄──────────────────────────┤
         │     (WebSocket)           │
         │                           │
         │  5. Show Result           │ 5. Show Result
         └───────────────────────────┘
```

## Key Technologies

- **QR Code**: `qrcode` library for generation
- **Real-Time**: `flask-socketio` for WebSocket communication
- **ML Model**: SGDClassifier for fraud detection
- **Frontend**: Responsive HTML/CSS/JavaScript

## API Endpoints

### `/generate-qr` (GET)
- Generates QR code for payment
- Returns QR code image and payment URL

### `/payment` (GET)
- Mobile payment interface
- Accessible via QR code scan

### `/api/predict` (POST)
- JSON API for fraud prediction
- Broadcasts result via WebSocket

**Request Body**:
```json
{
  "transaction_amount": 5000,
  "transaction_type": 0,
  "transaction_time": 14,
  "account_balance": 30000,
  "merchant_risk": 0.3
}
```

**Response**:
```json
{
  "fraud": false,
  "probability": 12.5,
  "status": "NORMAL",
  "timestamp": "2024-01-15T14:30:00"
}
```

## Troubleshooting

### QR Code Not Generating
```bash
pip install --upgrade qrcode[pil] pillow
```

### WebSocket Not Working
```bash
pip install --upgrade flask-socketio python-socketio
```

### Model Loading Error
```bash
python retrain_model.py
```

## Demo Workflow

1. **Open two browser windows**:
   - Window 1: Backend dashboard (after login)
   - Window 2: Mobile view (incognito/different browser)

2. **In Window 1**: Click "Generate Payment QR"

3. **In Window 2**: Navigate to the payment URL shown

4. **Fill payment details** in Window 2

5. **Click "Pay Now"**

6. **Watch both windows**: 
   - Window 2 shows payment result
   - Window 1 shows real-time notification

## Project Novelty

✨ **What makes this unique**:
- Real-time bidirectional fraud detection
- QR code-based payment simulation
- Simultaneous alerts on merchant and customer side
- Mobile-first payment interface
- One-pass online learning model

Perfect for demonstrating real-world fraud detection in payment systems!
