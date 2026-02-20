import pytest

from model_2.pattern_engine import analyze_patterns
from model_2.risk_aggregator import aggregate_risks
from model_2.model2_runner import run_model_2


def test_pattern_engine_multiple_matches():
    model1_out = {
        "ldl": {"status": "high"},
        "hdl": {"status": "low"},
    }

    patterns = [
        {"params": ["ldl:high", "hdl:low"], "count": 50, "tags": ["cardiac"]},
        {"params": ["ldl:high"], "count": 20, "tags": ["cardiac"]},
        {"params": ["glucose_fasting:high"], "count": 30, "tags": ["diabetes"]},
    ]

    summary = analyze_patterns(model1_out, patterns, total_reports=200)

    # Expect matched patterns to include the two cardiac patterns
    matched = summary.get("matched_patterns", [])
    assert any(set(p["params"]) == set(["ldl:high", "hdl:low"]) for p in matched)
    assert any(set(p["params"]) == set(["ldl:high"]) for p in matched)

    # Domain summary should contain cardiac
    domains = summary.get("domains", {})
    assert "cardiac" in domains


def test_risk_aggregator_conflicts_and_ordering():
    # conflicting patterns assigned to different tags
    matched = [
        {"params": ["ldl:high", "hdl:low"], "count": 50, "tags": ["cardiac"] , "confidence": 0.25},
        {"params": ["hdl:low", "glucose_fasting:high"], "count": 10, "tags": ["diabetes"] , "confidence": 0.05},
        {"params": ["ldl:high"], "count": 20, "tags": ["cardiac"] , "confidence": 0.1},
    ]

    domains = aggregate_risks(matched, total_reports=200)

    # cardiac should have higher severity than diabetes
    assert "cardiac" in domains
    assert "diabetes" in domains
    assert domains["cardiac"]["severity_score"] >= domains["diabetes"]["severity_score"]

    # matched patterns simplified format present
    assert isinstance(domains["cardiac"]["matched_patterns"], list)


def test_low_confidence_outputs():
    # patterns with very low counts relative to total_reports -> low confidence
    matched = [
        {"params": ["rare_param:abnormal"], "count": 1, "tags": ["general"], "confidence": 1.0 / 10000}
    ]

    domains = aggregate_risks(matched, total_reports=10000)
    gen = domains.get("general")
    assert gen is not None
    assert gen["confidence"] < 0.05


def test_model2_runner_handles_missing_values_and_no_patterns():
    # empty Model 1 output should not crash and should return default summary
    result = run_model_2({})

    assert "model_1" in result
    assert "model_2" in result
    domain_risks = result["model_2"].get("domain_risks", {})

    # No matched patterns -> domain_risks should be empty dict
    assert isinstance(domain_risks, dict)
    assert domain_risks == {}


def test_integration_multiple_matched_patterns_end_to_end():
    # end-to-end run with sample model1 output
    model1 = {
        "ldl": {"value": 160, "status": "high", "unit": "mg/dL"},
        "hdl": {"value": 35, "status": "low", "unit": "mg/dL"},
        "glucose_fasting": {"value": 110, "status": "pre_high", "unit": "mg/dL"}
    }

    # create a small patterns dataset inline by calling analyze_patterns + aggregate_risks
    patterns = [
        {"params": ["ldl:high", "hdl:low"], "count": 50, "tags": ["cardiac"], "confidence": 50/200},
        {"params": ["glucose_fasting:pre_high"], "count": 10, "tags": ["diabetes"], "confidence": 10/200}
    ]

    summary = analyze_patterns(model1, patterns, total_reports=200)
    matched = summary.get("matched_patterns", [])
    domains = aggregate_risks(matched, total_reports=200)

    assert "cardiac" in domains
    assert domains["cardiac"]["risk_level"] in ("low", "moderate", "high")
