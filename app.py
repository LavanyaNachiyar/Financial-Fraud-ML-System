import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import numpy as np
import qrcode
import io
import base64
from datetime import datetime
from sklearn.feature_extraction import DictVectorizer
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

model = joblib.load("online_sgd_model.pkl")
scaler = joblib.load("scaler.pkl")
vectorizer = joblib.load("vectorizer.pkl")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.Integer, nullable=False)
    transaction_time = db.Column(db.Integer, nullable=False)
    account_balance = db.Column(db.Float, nullable=False)
    merchant_risk = db.Column(db.Float, nullable=False)
    is_fraud = db.Column(db.Boolean, nullable=False)
    fraud_probability = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=True)

with app.app_context():
    db.create_all()

def login_required(func):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)

        user = User(username=username, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session["username"])

@app.route("/generate-qr")
@login_required
def generate_qr():
    payment_url = url_for("payment_page", _external=True)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(payment_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    
    return render_template("qr_code.html", qr_code=img_base64, payment_url=payment_url, ngrok_url=None)

@app.route("/payment")
def payment_page():
    return render_template("payment.html")

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    input_data = {}
    for key in request.form:
        val = request.form.get(key)
        input_data[key] = float(val) if val else 0.0

    X_vec = vectorizer.transform([input_data])
    X_scaled = scaler.transform(X_vec)
    prediction = model.predict(X_scaled)[0]
    proba = model.predict_proba(X_scaled)[0][1]

    if prediction == 1:
        result = "🚨 FRAUD TRANSACTION"
    else:
        result = "✅ NORMAL TRANSACTION"

    reasons = []
    if input_data.get("transaction_amount", 0) > 10000:
        reasons.append("🔴 High transaction amount detected")
    if input_data.get("login_attempts", 0) > 5:
        reasons.append("🔴 Multiple login attempts detected")
    if input_data.get("transaction_time", 12) < 5:
        reasons.append("🔴 Transaction at unusual hours")
    if input_data.get("vpn_used", 0) == 1:
        reasons.append("🔴 VPN usage detected")
    if input_data.get("merchant_risk", 0) < 0.5:
        reasons.append("🟢 Merchant risk is low")
    if not reasons:
        reasons.append("🟢 All values are within normal range")

    return render_template("result.html", result=result, probability=round(proba * 100, 2), features=input_data, reasons=reasons)

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json()
    input_data = {}
    for key in data:
        input_data[key] = float(data[key]) if data[key] else 0.0

    X_vec = vectorizer.transform([input_data])
    X_scaled = scaler.transform(X_vec)
    prediction = model.predict(X_scaled)[0]
    proba = model.predict_proba(X_scaled)[0][1]

    result = {"fraud": bool(prediction), "probability": round(proba * 100, 2), "status": "FRAUD" if prediction == 1 else "NORMAL", "timestamp": datetime.now().isoformat()}
    
    # Save transaction to database
    transaction = Transaction(
        user_id=session.get('user_id'),
        amount=input_data.get('transaction_amount', 0),
        transaction_type=int(input_data.get('transaction_type', 0)),
        transaction_time=int(input_data.get('transaction_time', 0)),
        account_balance=input_data.get('account_balance', 0),
        merchant_risk=input_data.get('merchant_risk', 0),
        is_fraud=bool(prediction),
        fraud_probability=round(proba * 100, 2),
        ip_address=request.remote_addr
    )
    db.session.add(transaction)
    db.session.commit()
    
    socketio.emit("transaction_result", result)
    return jsonify(result)

@app.route("/analytics")
@login_required
def analytics():
    total = Transaction.query.count()
    fraud_count = Transaction.query.filter_by(is_fraud=True).count()
    normal_count = total - fraud_count
    fraud_rate = (fraud_count / total * 100) if total > 0 else 0
    
    recent = Transaction.query.order_by(Transaction.timestamp.desc()).limit(10).all()
    
    stats = {
        'total': total,
        'fraud': fraud_count,
        'normal': normal_count,
        'fraud_rate': round(fraud_rate, 2)
    }
    
    return render_template("analytics.html", stats=stats, recent=recent)

@app.route("/transactions")
@login_required
def transactions():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template("transactions.html", transactions=transactions)

@app.route("/export-csv")
@login_required
def export_csv():
    import csv
    from io import StringIO
    from flask import make_response
    
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Amount', 'Type', 'Time', 'Balance', 'Merchant Risk', 'Fraud', 'Probability', 'Timestamp'])
    
    transactions = Transaction.query.all()
    for t in transactions:
        writer.writerow([t.id, t.amount, t.transaction_type, t.transaction_time, t.account_balance, t.merchant_risk, t.is_fraud, t.fraud_probability, t.timestamp])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=transactions.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/model-performance")
@login_required
def model_performance():
    import json
    try:
        with open('model_metrics.json', 'r') as f:
            metrics = json.load(f)
    except FileNotFoundError:
        metrics = None
    return render_template("model_performance.html", metrics=metrics)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
