from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import numpy as np
from sklearn.feature_extraction import DictVectorizer

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


model = joblib.load("online_sgd_model.pkl")
scaler = joblib.load("scaler.pkl")
vectorizer = joblib.load("vectorizer.pkl")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

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

    return render_template(
        "result.html",
        result=result,
        probability=round(proba * 100, 2),
        features=input_data,
        reasons=reasons
    )
if __name__ == "__main__":
    app.run(debug=True)
