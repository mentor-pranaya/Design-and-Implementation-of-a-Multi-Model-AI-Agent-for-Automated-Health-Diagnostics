from model_2.pattern_engine import analyze_patterns
from model_2.dataset_loader import load_lab_report_ds
from model_2.risk_aggregator import aggregate_risks
from model_2.features import generate_features
from model_2.ml_predictor import predict_risk
import os


def run_model_2(
    model1_output,
    datasets_base: str = "datasets/lab_report_ds",
    models_base: str = "models",
):
    """Run Model 2 hybrid risk analysis.

    - Loads historical patterns from `lab_report_ds` (via model_2 loader).
    - Matches Model 1 status flags against dataset patterns.
    - Produces per-domain (tag) risk, confidence, and explanations.
    - Uses ML models when available; otherwise falls back to pattern engine.
    """
    ds = load_lab_report_ds(datasets_base)
    patterns = ds.get("patterns", [])
    total_reports = ds.get("total_reports", 0)

    pattern_summary = analyze_patterns(model1_output, patterns, total_reports)

    # matched pattern list from pattern_summary
    matched = pattern_summary.get("matched_patterns", [])

    # Aggregate risks per domain using risk_aggregator
    pattern_domain_risks = aggregate_risks(matched, total_reports)

    # Generate derived features for downstream use / frontend display
    features = generate_features(model1_output or {})

    domain_risks = dict(pattern_domain_risks)

    cardiac_model_path = os.path.join(models_base, "cardiac_model.pkl")
    if os.path.exists(cardiac_model_path):
        cardiac_ml = predict_risk(features, cardiac_model_path)
        cardiac_ml.setdefault("matched_patterns", [])
        cardiac_ml.setdefault("reasons", ["ML model prediction"])
        domain_risks["cardiac"] = cardiac_ml

    diabetes_model_path = os.path.join(models_base, "diabetes_model.pkl")
    if os.path.exists(diabetes_model_path):
        diabetes_ml = predict_risk(features, diabetes_model_path)
        diabetes_ml.setdefault("matched_patterns", [])
        diabetes_ml.setdefault("reasons", ["ML model prediction"])
        domain_risks["diabetes"] = diabetes_ml

    # confidence_summary: pick top domain by confidence
    top_domain = None
    top_conf = 0.0
    for d, info in domain_risks.items():
        if info.get("confidence", 0.0) > top_conf:
            top_conf = info.get("confidence", 0.0)
            top_domain = d

    if top_domain and domain_risks.get(top_domain, {}).get("risk_level") != 'normal':
        confidence_summary = f"{domain_risks[top_domain]['risk_level'].capitalize()} risk for {top_domain} (confidence {domain_risks[top_domain]['confidence']})"
    else:
        confidence_summary = "No elevated risks detected with high confidence."

    # Build unified, frontend-ready schema
    return {
        "model_1": model1_output,
        "model_2": {
            "model": "Model 2 – Hybrid Risk Analysis",
            "pattern_summary": pattern_summary,
            "domain_risks": domain_risks,
            "features": features
        },
        "confidence_summary": confidence_summary
    }
