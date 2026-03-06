import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction import DictVectorizer

print("Loading dataset...")
df = pd.read_csv("dataset.csv")
y = df["label"].values
X_df = df.drop(columns=["label"])
X_dict = X_df.to_dict(orient="records")

print("Vectorizing features...")
vectorizer = DictVectorizer(sparse=False)
X_vectorized = vectorizer.fit_transform(X_dict)

print("Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_vectorized)

print("Training model (one-pass online learning)...")
model = SGDClassifier(loss="log_loss", learning_rate="optimal", max_iter=1, tol=None, random_state=42)
classes = np.array([0, 1])

for i in range(len(X_scaled)):
    model.partial_fit(X_scaled[i].reshape(1, -1), np.array([y[i]]), classes=classes)

print("Saving models...")
joblib.dump(model, "online_sgd_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ Model retrained and saved successfully!")
