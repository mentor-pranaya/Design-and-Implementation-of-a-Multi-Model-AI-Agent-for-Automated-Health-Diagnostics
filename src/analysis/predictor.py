import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.preprocessing import StandardScaler
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "enhanced_model.joblib")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.joblib")
FEATURE_ORDER = [
    "glucose", "cholesterol", "hemoglobin", "blood_pressure",
    "wbc", "platelets", "creatinine", "alt", "ast", "ldl", "hdl"
]

def generate_synthetic_data(n_samples=5000):
    """
    Generate larger, more realistic synthetic training data based on medical knowledge.
    """
    rng = np.random.RandomState(42)

    # Generate correlated features with realistic distributions (initial generation without upper clip for correlation)
    glucose = rng.normal(100, 15, n_samples).clip(70, None)  # Lower clip only
    cholesterol = rng.normal(180, 30, n_samples).clip(125, None)
    hemoglobin = rng.normal(14, 1.5, n_samples).clip(11, None)
    bp = rng.normal(120, 15, n_samples).clip(90, None)
    wbc = rng.normal(7500, 1500, n_samples).clip(4000, None)
    platelets = rng.normal(250000, 50000, n_samples).clip(150000, None)
    creatinine = rng.normal(0.9, 0.2, n_samples).clip(0.6, None)
    alt = rng.normal(25, 10, n_samples).clip(7, None)
    ast = rng.normal(25, 10, n_samples).clip(10, None)
    ldl = rng.normal(100, 20, n_samples).clip(50, None)
    hdl = rng.normal(50, 10, n_samples).clip(40, None)

    # Add some correlation between features
    # High glucose often correlates with high cholesterol
    high_glucose_mask = glucose > 120
    cholesterol[high_glucose_mask] += rng.normal(20, 10, high_glucose_mask.sum())

    # Anemia correlation
    low_hb_mask = hemoglobin < 12
    wbc[low_hb_mask] -= rng.normal(1000, 500, low_hb_mask.sum())

    # Re-clip after correlations to ensure ranges are maintained
    glucose = np.clip(glucose, 70, 140)
    cholesterol = np.clip(cholesterol, 125, 200)
    hemoglobin = np.clip(hemoglobin, 11, 16)
    bp = np.clip(bp, 90, 140)
    wbc = np.clip(wbc, 4000, 11000)
    platelets = np.clip(platelets, 150000, 450000)
    creatinine = np.clip(creatinine, 0.6, 1.2)
    alt = np.clip(alt, 7, 56)
    ast = np.clip(ast, 10, 40)
    ldl = np.clip(ldl, 50, 100)
    hdl = np.clip(hdl, 40, 60)

    # Create more sophisticated labels based on multiple risk factors
    risk_factors = (
        (glucose > 120) |
        (cholesterol > 200) |
        (ldl > 100) |
        (hdl < 40) |
        (hemoglobin < 12) |
        (creatinine > 1.2) |
        (alt > 40) |
        (ast > 35) |
        (wbc > 10000) |
        (platelets < 200000) |
        (bp > 130)
    )

    y = risk_factors.astype(int)

    X = np.vstack([glucose, cholesterol, hemoglobin, bp, wbc, platelets,
                   creatinine, alt, ast, ldl, hdl]).T

    return X, y

def _train_and_save():
    """
    Train enhanced model with comprehensive evaluation.
    """
    print("Generating synthetic training data...")
    X, y = generate_synthetic_data(5000)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Hyperparameter tuning
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    print("Performing hyperparameter tuning...")
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='f1', n_jobs=-1)
    grid_search.fit(X_train_scaled, y_train)

    best_model = grid_search.best_estimator_
    print(f"Best parameters: {grid_search.best_params_}")

    # Evaluate on test set
    y_pred = best_model.predict(X_test_scaled)
    print("\nModel Performance Metrics:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred):.4f}")
    print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")

    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Low Risk', 'High Risk']))

    # Cross-validation scores
    cv_scores = cross_val_score(best_model, X_train_scaled, y_train, cv=5, scoring='f1')
    print(f"\nCross-validation F1 scores: {cv_scores}")
    print(f"Mean CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

    # Save model and scaler
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    return best_model, scaler

def _load_model():
    """
    Load trained model and scaler, train if not exists.
    """
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        return model, scaler
    return _train_and_save()

def predict_risk(params: dict) -> dict:
    """
    Predict health risk with enhanced model.
    """
    try:
        if not isinstance(params, dict):
            raise ValueError("Input parameters must be a dictionary")

        model, scaler = _load_model()

        # Extract features
        x = []
        defaults = {
            "glucose": 110, "cholesterol": 190, "hemoglobin": 14, "blood_pressure": 120,
            "wbc": 7500, "platelets": 250000, "creatinine": 0.9, "alt": 25,
            "ast": 25, "ldl": 110, "hdl": 50
        }

        for f in FEATURE_ORDER:
            v = params.get(f)
            if v is None:
                v = defaults.get(f, 0)
            try:
                x.append(float(v))
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid value for parameter '{f}': {v} - {str(e)}")

        # Scale and predict
        arr = np.array(x).reshape(1, -1)
        arr_scaled = scaler.transform(arr)
        prob = float(model.predict_proba(arr_scaled)[0][1])

        # Determine risk level with more granularity
        if prob >= 0.8:
            label = "very_high"
        elif prob >= 0.6:
            label = "high"
        elif prob >= 0.4:
            label = "moderate"
        elif prob >= 0.2:
            label = "low_moderate"
        else:
            label = "low"

        return {
            "risk_score": round(prob, 4),
            "risk_label": label,
            "confidence": "high" if prob > 0.7 or prob < 0.3 else "medium"
        }
    except Exception as e:
        raise RuntimeError(f"Risk prediction failed: {str(e)}")

def evaluate_model_on_data(X_test, y_test):
    """
    Evaluate model performance on given test data.
    """
    model, scaler = _load_model()
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred)
    }
