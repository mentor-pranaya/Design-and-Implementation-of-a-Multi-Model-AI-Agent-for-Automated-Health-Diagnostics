"""
Main Orchestrator - Coordinates full health report analysis pipeline.

Routes data through Model 1 (NER/Parameter Extraction), Model 2 (Risk Scoring),
Model 3 (Risk Adjustment), and Report Generation (Findings + Recommendations).
"""

import logging
from typing import Any, Dict, Optional

from model_1.model1_runner import run_model_1
from model_2.model2_runner import run_model_2
from model_3.model3_runner import run_model_3
from reporting.finding_synthesizer import synthesize_findings
from reporting.recommendation_engine import generate_recommendations
from reporting.report_formatter import format_report

logger = logging.getLogger(__name__)


def generate_full_report_with_outputs(
    input_data: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run the full pipeline and return report plus model outputs.
    
    Process:
    1. Extract key abnormalities from structuring phase (if present)
    2. Run Model 1 for NER/extraction (may be skipped if structuring provided it)
    3. Run Model 2 for risk scoring
    4. Run Model 3 for risk adjustment
    5. Synthesize findings from all sources
    6. Generate recommendations
    7. Format final report
    
    Args:
        input_data: Structured medical data from Phase 2 or raw data
        user_context: Patient context (age, gender, medical history, etc.)
    
    Returns:
        Dictionary with 'report', 'model_1', 'model_2', 'model_3' outputs
    """
    user_context = user_context or {}
    errors = []
    
    logger.info("Starting full report generation pipeline")
    
    # Extract any abnormalities that came from the structuring phase
    # (new production pipeline passes these directly)
    extraction_abnormalities = input_data.get('key_abnormalities', [])
    if extraction_abnormalities:
        logger.info(f"Found {len(extraction_abnormalities)} abnormalities from structuring phase")
    
    try:
        logger.info("Step 1: Running Model 1 (NER/Parameter Extraction)")
        model1_output = run_model_1(input_data or {})
        
        # Merge abnormalities from structuring phase if Model 1 didn't find them
        if extraction_abnormalities and not model1_output.get('key_abnormalities'):
            model1_output['key_abnormalities'] = extraction_abnormalities
            logger.info("Added structuring abnormalities to Model 1 output")
            
    except Exception as exc:
        model1_output = {}
        errors.append(f"model_1_error: {exc}")
        logger.error(f"Model 1 error: {exc}")
        
        # If Model 1 fails, use structuring abnormalities if available
        if extraction_abnormalities:
            model1_output = {'key_abnormalities': extraction_abnormalities}
            logger.info("Using structuring abnormalities as fallback")

    try:
        logger.info("Step 2: Running Model 2 (Risk Scoring)")
        model2_output = run_model_2(model1_output)
    except Exception as exc:
        model2_output = {"model_2": {"domain_risks": {}}}
        errors.append(f"model_2_error: {exc}")
        logger.error(f"Model 2 error: {exc}")

    domain_risks = {}
    if isinstance(model2_output, dict):
        domain_risks = (model2_output.get("model_2") or {}).get("domain_risks") or {}
    
    logger.info(f"Model 2 produced {len(domain_risks)} domain risks")

    try:
        logger.info("Step 3: Running Model 3 (Risk Adjustment)")
        model3_output = run_model_3(model1_output, domain_risks, user_context)
    except Exception as exc:
        model3_output = {"adjusted_risks": domain_risks}
        errors.append(f"model_3_error: {exc}")
        logger.error(f"Model 3 error: {exc}")

    logger.info("Step 4: Synthesizing findings")
    synthesized = synthesize_findings(model1_output, model3_output)
    
    logger.info("Step 5: Generating recommendations")
    recommendations = generate_recommendations(synthesized, user_context)
    
    logger.info("Step 6: Formatting final report")
    report = format_report(synthesized, recommendations)

    if errors and report.get("summary"):
        logger.warning(f"Pipeline had {len(errors)} errors during processing")
        report["summary"] = (
            f"{report['summary']} Some data sources were unavailable during processing."
        )
    else:
        logger.info("Pipeline completed successfully")

    return {
        "report": report,
        "model_1": model1_output,
        "model_2": model2_output,
        "model_3": model3_output,
    }


def generate_full_report(
    input_data: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run the full pipeline and return a frontend-ready report JSON.
    
    Args:
        input_data: Structured medical data
        user_context: Patient context
    
    Returns:
        Formatted report dictionary ready for frontend
    """
    outputs = generate_full_report_with_outputs(input_data, user_context)
    return outputs["report"]

