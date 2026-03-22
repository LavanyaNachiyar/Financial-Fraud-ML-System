import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from flask_socketio import SocketIO, emit
from supabase import create_client, Client
import joblib
import numpy as np
import qrcode
import io
import base64
import csv
import json
from datetime import datetime, timezone
from sklearn.feature_extraction import DictVectorizer
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or "supersecretkey"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

socketio = SocketIO(app, cors_allowed_origins="*")

model = joblib.load("online_sgd_model.pkl")
scaler = joblib.load("scaler.pkl")
vectorizer = joblib.load("vectorizer.pkl")
print("Models loaded successfully")


def login_required(func):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/auth/callback")
def auth_callback():
    # Handles magic link clicks - extracts session from URL fragment via JS
    return render_template("auth_callback.html")


@app.route("/auth/session", methods=["POST"])
def auth_session():
    access_token = request.json.get("access_token")
    try:
        user_response = supabase.auth.get_user(access_token)
        auth_user = user_response.user
        email = auth_user.email

        existing = supabase.table("users").select("*").eq("email", email).execute()
        if existing.data:
            user = existing.data[0]
        else:
            username = email.split("@")[0]
            result = supabase.table("users").insert({"username": username, "email": email}).execute()
            user = result.data[0]

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return jsonify({"redirect": url_for("index")})
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@app.route("/register")
def register():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        try:
            supabase.auth.sign_in_with_otp({
                "email": email,
                "options": {
                    "should_create_user": True,
                    "email_redirect_to": "https://financial-fraud-ml-system.onrender.com/auth/callback"
                }
            })
            session["otp_email"] = email
            return redirect(url_for("verify_otp"))
        except Exception as e:
            flash(f"Failed to send link: {str(e)}", "danger")
    return render_template("login.html")


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "otp_email" not in session:
        return redirect(url_for("login"))
    return render_template("verify_otp.html")


@app.route("/auth/check")
def auth_check():
    if "user_id" in session:
        return jsonify({"logged_in": True})
    return jsonify({"logged_in": False})


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

    result = "🚨 FRAUD TRANSACTION" if prediction == 1 else "✅ NORMAL TRANSACTION"

    supabase.table("transactions").insert({
        "user_id": session.get("user_id"),
        "amount": input_data.get("transaction_amount", 0),
        "transaction_type": int(input_data.get("transaction_type", 0)),
        "transaction_time": int(input_data.get("transaction_time", 0)),
        "account_balance": input_data.get("account_balance", 0),
        "merchant_risk": input_data.get("merchant_risk", 0),
        "is_fraud": bool(prediction),
        "fraud_probability": round(proba * 100, 2),
        "ip_address": request.remote_addr,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }).execute()

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
    input_data = {key: float(data[key]) if data[key] else 0.0 for key in data}

    X_vec = vectorizer.transform([input_data])
    X_scaled = scaler.transform(X_vec)
    prediction = model.predict(X_scaled)[0]
    proba = model.predict_proba(X_scaled)[0][1]

    result = {
        "fraud": bool(prediction),
        "probability": round(proba * 100, 2),
        "status": "FRAUD" if prediction == 1 else "NORMAL",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    supabase.table("transactions").insert({
        "user_id": session.get("user_id"),
        "amount": input_data.get("transaction_amount", 0),
        "transaction_type": int(input_data.get("transaction_type", 0)),
        "transaction_time": int(input_data.get("transaction_time", 0)),
        "account_balance": input_data.get("account_balance", 0),
        "merchant_risk": input_data.get("merchant_risk", 0),
        "is_fraud": bool(prediction),
        "fraud_probability": round(proba * 100, 2),
        "ip_address": request.remote_addr,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }).execute()

    socketio.emit("transaction_result", result)
    return jsonify(result)


@app.route("/analytics")
@login_required
def analytics():
    all_tx = supabase.table("transactions").select("*").execute().data
    for t in all_tx:
        if isinstance(t.get("timestamp"), str):
            t["timestamp"] = datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))

    total = len(all_tx)
    fraud_count = sum(1 for t in all_tx if t["is_fraud"])
    normal_count = total - fraud_count
    fraud_rate = round(fraud_count / total * 100, 2) if total > 0 else 0

    recent = sorted(all_tx, key=lambda x: x["timestamp"], reverse=True)[:10]

    stats = {"total": total, "fraud": fraud_count, "normal": normal_count, "fraud_rate": fraud_rate}
    return render_template("analytics.html", stats=stats, recent=recent)


@app.route("/transactions")
@login_required
def transactions():
    page = request.args.get("page", 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    result = supabase.table("transactions").select("*", count="exact").order("timestamp", desc=True).range(offset, offset + per_page - 1).execute()
    total = result.count or 0
    pages = max(1, (total + per_page - 1) // per_page)

    # Parse timestamp strings to datetime objects
    items = result.data
    for t in items:
        if isinstance(t.get("timestamp"), str):
            t["timestamp"] = datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))

    class Pagination:
        def __init__(self, items, page, per_page, total, pages):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = pages
            self.has_prev = page > 1
            self.has_next = page < pages
            self.prev_num = page - 1
            self.next_num = page + 1

        def iter_pages(self, left_edge=1, right_edge=1, left_current=1, right_current=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (self.page - left_current - 1 < num < self.page + right_current) or
                        num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    return render_template("transactions.html", transactions=Pagination(items, page, per_page, total, pages))


@app.route("/export-csv")
@login_required
def export_csv():
    from io import StringIO
    all_tx = supabase.table("transactions").select("*").execute().data

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "Amount", "Type", "Time", "Balance", "Merchant Risk", "Fraud", "Probability", "Timestamp"])
    for t in all_tx:
        writer.writerow([t["id"], t["amount"], t["transaction_type"], t["transaction_time"],
                         t["account_balance"], t["merchant_risk"], t["is_fraud"], t["fraud_probability"], t["timestamp"]])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=transactions.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route("/model-performance")
@login_required
def model_performance():
    try:
        with open("model_metrics.json", "r") as f:
            metrics = json.load(f)
    except FileNotFoundError:
        metrics = None
    return render_template("model_performance.html", metrics=metrics)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
