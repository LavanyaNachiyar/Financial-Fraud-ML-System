# One Pass Learning - Fraud Detection System

A machine learning-based fraud detection web application using online learning with SGDClassifier. The model learns incrementally in a single pass through the data.

## Features

- **One-Pass Online Learning**: Trains on data incrementally using SGDClassifier
- **User Authentication**: Secure login/registration system
- **Real-time Predictions**: Fraud detection with probability scores
- **Risk Analysis**: Identifies suspicious transaction patterns

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **ML**: scikit-learn (SGDClassifier, StandardScaler, DictVectorizer)
- **Data**: pandas, numpy
- **Model Persistence**: joblib

## Installation

1. Install dependencies:
```bash
pip install -r req.txt
```

2. Train the model (run the Jupyter notebook):
```bash
jupyter notebook onepass.ipynb
```

3. Run the Flask app:
```bash
python app.py
```

4. Access at `http://localhost:5000`

## Project Structure

```
├── app.py                    # Flask web application
├── onepass.ipynb            # Model training notebook
├── templates/               # HTML templates
├── instance/                # SQLite database (auto-generated)
├── *.pkl                    # Trained models (auto-generated)
└── dataset.csv              # Training data
```

## Usage

1. Register/Login to access the system
2. Enter transaction details
3. Get fraud prediction with risk analysis

## Model Details

- **Algorithm**: SGDClassifier with logistic loss
- **Training**: One-pass incremental learning using partial_fit
- **Features**: Transaction amount, login attempts, time, VPN usage, merchant risk, etc.
- **Output**: Binary classification (Fraud/Normal) with probability

## License

MIT
