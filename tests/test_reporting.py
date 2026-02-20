import pytest

from reporting.finding_synthesizer import synthesize_findings
from reporting.recommendation_engine import generate_recommendations
from reporting.report_formatter import format_report
from main_orchestrator import generate_full_report


def test_synthesize_findings():
    model1_output = {
        "ldl": {"status": "high", "value": 180, "unit": "mg/dL"},
        "hdl": {"status": "normal", "value": 50, "unit": "mg/dL"},
        "glucose": {"status": "low", "value": 60, "unit": "mg/dL"},
    }
    model3_output = {
        "adjusted_risks": {
            "cardiac": {
                "risk_level": "high",
                "severity_score": 0.9,
                "confidence": 0.8,
            },
            "diabetes": {
                "risk_level": "moderate",
                "severity_score": 0.4,
                "confidence": 0.5,
            },
            "cbc": {
                "risk_level": "normal",
                "severity_score": 0.2,
                "confidence": 0.6,
            },
        }
    }

    synthesized = synthesize_findings(model1_output, model3_output)

    abnormalities = synthesized.get("key_abnormalities", [])
    assert any(item.get("parameter") == "ldl" for item in abnormalities)
    assert any(item.get("parameter") == "glucose" for item in abnormalities)
    assert all(item.get("parameter") != "hdl" for item in abnormalities)

    risks = synthesized.get("risk_summary", [])
    assert len(risks) == 2
    assert risks[0].get("domain") == "cardiac"
    assert risks[0].get("risk_level") == "high"


def test_generate_recommendations():
    synthesized_findings = {
        "key_abnormalities": [],
        "risk_summary": [
            {"domain": "cardiac", "risk_level": "high", "severity_score": 0.8},
        ],
    }
    user_context = {"smoker": True}

    result = generate_recommendations(synthesized_findings, user_context)

    recs = result.get("recommendations", [])
    assert any("smoking" in rec.lower() for rec in recs)
    assert result.get("urgency_level") == "high"


def test_format_report():
    synthesized = {
        "overall_assessment": "Sample summary.",
        "key_abnormalities": [{"parameter": "ldl", "status": "high"}],
        "risk_summary": [{"domain": "cardiac", "risk_level": "high"}],
    }
    recommendations = {
        "recommendations": ["Consult a cardiologist."],
        "urgency_level": "high",
    }

    report = format_report(synthesized, recommendations)

    assert "summary" in report
    assert "key_findings" in report
    assert "risks" in report
    assert "recommendations" in report
    assert "disclaimer" in report


def test_full_orchestrator(monkeypatch):
    def mock_model_1(input_data):
        return {"ldl": {"status": "high", "value": 180}}

    def mock_model_2(model1_output):
        return {
            "model_2": {
                "domain_risks": {
                    "cardiac": {"risk_level": "high", "severity_score": 0.9}
                }
            }
        }

    def mock_model_3(model1_output, domain_risks, user_context):
        return {"adjusted_risks": domain_risks}

    monkeypatch.setattr("main_orchestrator.run_model_1", mock_model_1)
    monkeypatch.setattr("main_orchestrator.run_model_2", mock_model_2)
    monkeypatch.setattr("main_orchestrator.run_model_3", mock_model_3)

    report = generate_full_report({"ldl": {"value": 180}}, user_context=None)

    assert isinstance(report, dict)
    assert "summary" in report
    assert "key_findings" in report
    assert "risks" in report
    assert "recommendations" in report
    assert "disclaimer" in report


def test_generate_recommendations_empty_inputs():
    result = generate_recommendations({"key_abnormalities": [], "risk_summary": []}, None)
    assert result.get("urgency_level") == "low"
    assert isinstance(result.get("recommendations"), list)
