"""ML predictor for Model 2 risk inference."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import joblib

from model_2.features import FEATURE_ORDER


def _vectorize_features(feature_dict: Dict[str, Any], feature_names: List[str]) -> List[float]:
    vector: List[float] = []
    for name in feature_names:
        val = feature_dict.get(name)
        if isinstance(val, bool):
            vector.append(1.0 if val else 0.0)
        elif val is None:
            vector.append(0.0)
        else:
            try:
                vector.append(float(val))
            except Exception:
                vector.append(0.0)
    return vector


def _risk_level_from_prob(prob: float) -> str:
    if prob >= 0.7:
        return "high"
    if prob >= 0.4:
        return "moderate"
    if prob >= 0.2:
        return "low"
    return "normal"


def _top_features_by_contribution(contribs: Dict[str, float], top_k: int = 3) -> List[Dict[str, float]]:
    ranked = sorted(contribs.items(), key=lambda kv: abs(kv[1]), reverse=True)[:top_k]
    return [{"feature": k, "contribution": float(v)} for k, v in ranked]


def _top_features_by_importance(importances: Dict[str, float], top_k: int = 3) -> List[Dict[str, float]]:
    ranked = sorted(importances.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [{"feature": k, "importance": float(v)} for k, v in ranked]


def predict_risk(
    feature_dict: Dict[str, Any],
    model_path: str,
    feature_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    payload = joblib.load(model_path)
    if isinstance(payload, dict) and "model" in payload:
        model = payload["model"]
        model_type = payload.get("model_type")
        feature_names = payload.get("feature_names") or feature_names
    else:
        model = payload
        model_type = None

    feature_names = feature_names or list(FEATURE_ORDER)
    vector = _vectorize_features(feature_dict, feature_names)

    prob = None
    if hasattr(model, "predict_proba"):
        prob = float(model.predict_proba([vector])[0][1])
    elif hasattr(model, "decision_function"):
        score = float(model.decision_function([vector])[0])
        prob = 1.0 / (1.0 + pow(2.718281828, -score))
    else:
        pred = int(model.predict([vector])[0])
        prob = 1.0 if pred == 1 else 0.0

    risk_level = _risk_level_from_prob(prob)
    confidence = prob if prob >= 0.5 else 1.0 - prob

    explainability: Dict[str, Any] = {}
    if model_type == "logistic_regression" and hasattr(model, "coef_"):
        coefs = model.coef_[0].tolist()
        coef_map = {name: float(coef) for name, coef in zip(feature_names, coefs)}
        contribs = {name: coef_map[name] * vector[i] for i, name in enumerate(feature_names)}
        explainability = {
            "method": "logistic_regression",
            "feature_coefficients": coef_map,
            "top_features": _top_features_by_contribution(contribs),
        }
    elif hasattr(model, "feature_importances_"):
        imps = model.feature_importances_.tolist()
        imp_map = {name: float(imp) for name, imp in zip(feature_names, imps)}
        explainability = {
            "method": "random_forest",
            "feature_importances": imp_map,
            "top_features": _top_features_by_importance(imp_map),
        }

    return {
        "risk_level": risk_level,
        "severity_score": round(float(prob), 3),
        "confidence": round(float(confidence), 3),
        "source": "ml_model",
        "explainability": explainability,
    }
