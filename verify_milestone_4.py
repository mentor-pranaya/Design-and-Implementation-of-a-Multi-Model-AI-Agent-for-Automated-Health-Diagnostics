import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add src to path
sys.path.append(os.getcwd())

async def verify_milestone_4():
    print("--- Verifying Milestone 4 (Full Integration & Reporting) ---")
    
    # 1. Test Refactored Orchestrator Logic
    # We will test the orchestrator indirectly via the API logic logic or directly
    from src.agent.agent_orchestrator import MultiAgentOrchestrator
    
    orchestrator = MultiAgentOrchestrator()
    
    # Mock internal agents to avoid full execution overhead/external calls
    mock_intent = MagicMock()
    mock_intent.inferred_intent = 'analyze_blood_report'
    mock_intent.confidence_score = 1.0
    orchestrator.intent_inference_agent.analyze_intent = AsyncMock(return_value=mock_intent)

    
    def mock_result(data):
        m = MagicMock()
        m.success = True
        m.data = data
        m.execution_time = 0.1
        return m

    orchestrator.extraction_agent.execute = MagicMock(return_value=mock_result({"Glucose": {"value": 150, "unit": "mg/dL"}}))
    orchestrator.interpretation_agent.execute = MagicMock(return_value=mock_result(["High Glucose"]))
    orchestrator.risk_analysis_agent.execute = MagicMock(return_value=mock_result({"derived_metrics": {}, "risk_indicators": ["Diabetes Risk"]}))
    orchestrator.context_analysis_agent.execute = MagicMock(return_value=mock_result({"context_adjustments": []}))
    orchestrator.prediction_agent.execute = MagicMock(return_value=mock_result({"risk_score": 0.8}))
    orchestrator.recommendation_agent.execute = MagicMock(return_value=mock_result([{"recommendation": "Diet", "finding": "High Glucose"}]))
    orchestrator.prescription_agent.execute = MagicMock(return_value=mock_result([]))
    orchestrator.synthesis_agent.execute = MagicMock(return_value=mock_result("Patient has high glucose."))

    print("Running Orchestrator.execute...")
    report = await orchestrator.execute({"Glucose": 150})
    
    if report.status == "success" and "Diabetes Risk" in report.risks:
        print("[PASS] Orchestrator successfully integrated all models.")
    else:
        print(f"[FAIL] Orchestrator failed or missing risks: {report.status}")

    # 2. Test PDF Generation
    from src.reporting.pdf_generator import PDFReportGenerator
    
    pdf_gen = PDFReportGenerator()
    data = {
        "synthesis": "This is a test summary.",
        "overall_risk": "Moderate",
        "risks": ["Risk A", "Risk B"],
        "extracted_parameters": {"Glucose": {"value": 100, "unit": "mg/dL"}},
        "interpretations": ["Normal Glucose"],
        "linked_recommendations": [{"recommendation": "Stay healthy", "finding": "General"}]
    }
    
    print("Generating PDF report...")
    try:
        path = pdf_gen.generate_pdf_report(data, "test_report.pdf")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"[PASS] PDF generated successfully at {path} ({os.path.getsize(path)} bytes)")
        else:
            print("[FAIL] PDF file not found or empty.")
    except Exception as e:
        print(f"[FAIL] PDF generation crashed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_milestone_4())
