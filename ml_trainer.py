"""Train ML models for Model 2 risk prediction."""
from __future__ import annotations

import argparse
import csv
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

from model_2.features import FEATURE_ORDER, generate_features


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _load_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def _discover_dataset_file(base_path: str) -> str:
    if os.path.isfile(base_path):
        return base_path

    candidates = [
        "structured_records.json",
        "structured_records.jsonl",
        "structured_records.csv",
        "records.json",
        "records.jsonl",
        "records.csv",
        "lab_reports.json",
        "lab_reports.jsonl",
        "lab_reports.csv",
        "dataset.json",
        "dataset.jsonl",
        "dataset.csv",
    ]
    for name in candidates:
        cand = os.path.join(base_path, name)
        if os.path.exists(cand):
            return cand

    raise FileNotFoundError(
        "No structured dataset found. Provide a file path or place a structured "
        "dataset in the base directory with a supported name (json/jsonl/csv)."
    )


def _load_records(base_path: str) -> List[Dict[str, Any]]:
    dataset_path = _discover_dataset_file(base_path)
    if dataset_path.endswith(".jsonl"):
        return _load_jsonl(dataset_path)
    if dataset_path.endswith(".json"):
        data = _load_json(dataset_path)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "records" in data:
            return data["records"]
        raise ValueError("JSON dataset must be a list or contain a 'records' list")
    if dataset_path.endswith(".csv"):
        return _load_csv(dataset_path)
    raise ValueError("Unsupported dataset format: " + dataset_path)


def _parse_model1_output(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for key in ("model1_output", "model_1", "model1", "parameters", "lab_results"):
        if key in record:
            val = record.get(key)
            if isinstance(val, dict):
                return val
            if isinstance(val, str) and val.strip().startswith("{"):
                try:
                    return json.loads(val)
                except Exception:
                    return None
    return None


def _normalize_label(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return 1 if float(value) >= 1 else 0
    if isinstance(value, str):
        val = value.strip().lower()
        if val in ("1", "true", "yes", "positive", "pos"):
            return 1
        if val in ("0", "false", "no", "negative", "neg"):
            return 0
        if val in ("high", "moderate", "medium", "severe"):
            return 1
        if val in ("low", "normal", "mild", "none"):
            return 0
    return None


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


def _evaluate_model(model, x_test, y_test) -> Dict[str, Optional[float]]:
    pred = model.predict(x_test)
    metrics: Dict[str, Optional[float]] = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "roc_auc": None,
    }
    try:
        prob = model.predict_proba(x_test)[:, 1]
        metrics["roc_auc"] = float(roc_auc_score(y_test, prob))
    except Exception:
        metrics["roc_auc"] = None
    return metrics


def _pick_best_model(results: List[Tuple[str, Dict[str, Optional[float]], Any]]) -> Tuple[str, Dict[str, Optional[float]], Any]:
    best = None
    for name, metrics, model in results:
        key = metrics.get("roc_auc")
        if key is None:
            key = metrics.get("accuracy")
        if best is None:
            best = (name, metrics, model, key)
        else:
            if key is not None and key > best[3]:
                best = (name, metrics, model, key)
    return best[0], best[1], best[2]


def _train_domain_model(x: np.ndarray, y: np.ndarray) -> Tuple[str, Dict[str, Optional[float]], Any]:
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y if len(set(y.tolist())) > 1 else None,
    )

    models = [
        ("logistic_regression", LogisticRegression(max_iter=1000)),
        ("random_forest", RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")),
    ]

    results = []
    for name, model in models:
        model.fit(x_train, y_train)
        metrics = _evaluate_model(model, x_test, y_test)
        results.append((name, metrics, model))

    return _pick_best_model(results)


def train_models(
    dataset_base: str,
    models_dir: str = "models",
    cardiac_label_col: str = "cardiac_label",
    diabetes_label_col: str = "diabetes_label",
) -> Dict[str, Any]:
    records = _load_records(dataset_base)

    feature_names = list(FEATURE_ORDER)
    cardiac_rows: List[Tuple[List[float], int]] = []
    diabetes_rows: List[Tuple[List[float], int]] = []

    for record in records:
        model1_output = _parse_model1_output(record)
        if not model1_output:
            continue
        features = generate_features(model1_output)
        vector = _vectorize_features(features, feature_names)

        cardiac_label = _normalize_label(record.get(cardiac_label_col))
        if cardiac_label is not None:
            cardiac_rows.append((vector, cardiac_label))

        diabetes_label = _normalize_label(record.get(diabetes_label_col))
        if diabetes_label is not None:
            diabetes_rows.append((vector, diabetes_label))

    results: Dict[str, Any] = {}
    os.makedirs(models_dir, exist_ok=True)

    for domain, rows, out_name in (
        ("cardiac", cardiac_rows, "cardiac_model.pkl"),
        ("diabetes", diabetes_rows, "diabetes_model.pkl"),
    ):
        if not rows:
            results[domain] = {"error": "No labeled rows found for training."}
            continue

        x = np.array([r[0] for r in rows], dtype=float)
        y = np.array([r[1] for r in rows], dtype=int)
        if len(set(y.tolist())) < 2:
            results[domain] = {"error": "Need at least two classes to train."}
            continue

        model_type, metrics, model = _train_domain_model(x, y)

        payload = {
            "model": model,
            "feature_names": feature_names,
            "model_type": model_type,
            "metrics": metrics,
            "domain": domain,
        }

        out_path = os.path.join(models_dir, out_name)
        joblib.dump(payload, out_path)

        results[domain] = {
            "model_type": model_type,
            "metrics": metrics,
            "model_path": out_path,
        }

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Model 2 ML classifiers")
    parser.add_argument("--data", required=True, help="Path to structured dataset or dataset directory")
    parser.add_argument("--models-dir", default="models", help="Output directory for trained models")
    parser.add_argument("--cardiac-label", default="cardiac_label", help="Column for cardiac label")
    parser.add_argument("--diabetes-label", default="diabetes_label", help="Column for diabetes label")
    args = parser.parse_args()

    results = train_models(
        dataset_base=args.data,
        models_dir=args.models_dir,
        cardiac_label_col=args.cardiac_label,
        diabetes_label_col=args.diabetes_label,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
