import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction import DictVectorizer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

print("Evaluating model performance...")

# Load model and data
model = joblib.load("online_sgd_model.pkl")
scaler = joblib.load("scaler.pkl")
vectorizer = joblib.load("vectorizer.pkl")
df = pd.read_csv("dataset.csv")

# Prepare data
y_true = df["label"].values
X_df = df.drop(columns=["label"])
X_dict = X_df.to_dict(orient="records")
X_vectorized = vectorizer.transform(X_dict)
X_scaled = scaler.transform(X_vectorized)

# Predictions
y_pred = model.predict(X_scaled)
y_proba = model.predict_proba(X_scaled)[:, 1]

# Calculate metrics
metrics = {
    "accuracy": round(accuracy_score(y_true, y_pred) * 100, 2),
    "precision": round(precision_score(y_true, y_pred) * 100, 2),
    "recall": round(recall_score(y_true, y_pred) * 100, 2),
    "f1_score": round(f1_score(y_true, y_pred) * 100, 2)
}

# Confusion Matrix
cm = confusion_matrix(y_true, y_pred)
metrics["confusion_matrix"] = cm.tolist()
metrics["true_negatives"] = int(cm[0][0])
metrics["false_positives"] = int(cm[0][1])
metrics["false_negatives"] = int(cm[1][0])
metrics["true_positives"] = int(cm[1][1])

# ROC Curve
fpr, tpr, thresholds = roc_curve(y_true, y_proba)
roc_auc = auc(fpr, tpr)
metrics["roc_auc"] = round(roc_auc * 100, 2)

# Save metrics
with open("model_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

# Generate Confusion Matrix Plot
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
plt.title('Confusion Matrix')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('static/confusion_matrix.png', dpi=100, bbox_inches='tight')
plt.close()

# Generate ROC Curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend(loc="lower right")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('static/roc_curve.png', dpi=100, bbox_inches='tight')
plt.close()

# Feature Importance (coefficients)
feature_names = vectorizer.get_feature_names_out()
coefficients = model.coef_[0]
feature_importance = sorted(zip(feature_names, coefficients), key=lambda x: abs(x[1]), reverse=True)[:10]

plt.figure(figsize=(10, 6))
features, importances = zip(*feature_importance)
plt.barh(features, importances, color='steelblue')
plt.xlabel('Coefficient Value')
plt.title('Top 10 Feature Importance')
plt.tight_layout()
plt.savefig('static/feature_importance.png', dpi=100, bbox_inches='tight')
plt.close()

print("\n✅ Model evaluation complete!")
print(f"Accuracy: {metrics['accuracy']}%")
print(f"Precision: {metrics['precision']}%")
print(f"Recall: {metrics['recall']}%")
print(f"F1-Score: {metrics['f1_score']}%")
print(f"ROC-AUC: {metrics['roc_auc']}%")
print("\nMetrics saved to: model_metrics.json")
print("Visualizations saved to: static/")
