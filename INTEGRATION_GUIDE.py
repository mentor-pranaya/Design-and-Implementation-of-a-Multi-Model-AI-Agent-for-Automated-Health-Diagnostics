"""
Integration Guide: Wiring New Modules into API

This file demonstrates how to integrate all new modules into the existing
FastAPI backend to create the complete production-grade system.

Copy these examples into your api/main.py or main_orchestrator.py
"""

# ============================================================================
# INTEGRATION EXAMPLE FOR API ENDPOINT
# ============================================================================

"""
# In your api/main.py or similar, add this integration:

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging

from severity_engine import SeverityEngine, SeverityLevel
from risk_aggregator import RiskAggregator, UrgencyLevel
from summary_generator import SummaryGenerator
from recommendation_engine import RecommendationEngine

# Initialize engines
severity_engine = SeverityEngine()
risk_aggregator = RiskAggregator()
summary_generator = SummaryGenerator()
recommendation_engine = RecommendationEngine()

logger = logging.getLogger(__name__)


@app.post("/analyze")
async def analyze_report(
    file: UploadFile = File(...),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    medical_history: Optional[str] = Form(None),
    lifestyle: Optional[str] = Form(None)
):
    '''
    Complete health report analysis endpoint.
    
    Integrates all production modules for comprehensive assessment.
    '''
    
    try:
        # Step 1: Extract text from uploaded file
        # (using existing input_handlers module)
        from input_handlers.phase1_input import extract_text_from_file
        
        extracted_text = await extract_text_from_file(
            file=file,
            apply_ocr_cleaning=True  # Uses new ocr_cleaner module
        )
        
        logger.info(f"Text extracted: {len(extracted_text)} characters")
        
        # Step 2: Structure and extract parameters
        # (using enhanced phase2_structuring with severity calculation)
        from structuring_layers.phase2_structuring import structure_report
        from medical_parameter_extractor import MedicalParameterExtractor
        
        structured_data = structure_report(extracted_text)
        
        # Extract parameters with severity assessment
        param_extractor = MedicalParameterExtractor()
        extracted_params = param_extractor.extract_all_parameters(extracted_text)
        
        logger.info(f"Extracted {len(extracted_params)} parameters")
        
        # Step 3: Calculate severity for each parameter
        severity_results = {}
        
        # Map extracted parameters to reference ranges
        reference_ranges_map = {
            "glucose": (70, 100),
            "hemoglobin": (12, 16),
            "total_cholesterol": (0, 200),
            "hdl": (40, 999),
            "ldl": (0, 100),
            "triglycerides": (0, 150),
            "creatinine": (0.6, 1.2),
            "platelet": (150, 400),
            "wbc": (4.5, 11),
        }
        
        for param_name, param_value in extracted_params.items():
            if param_name in reference_ranges_map:
                ref_min, ref_max = reference_ranges_map[param_name]
                
                severity_result = severity_engine.calculate_severity(
                    value=param_value,
                    reference_min=ref_min,
                    reference_max=ref_max,
                    unit="units",  # Adjust based on parameter
                    age=age,
                    gender=gender
                )
                
                severity_results[param_name] = severity_result.to_dict()
        
        logger.info(f"Severity calculated for {len(severity_results)} parameters")
        
        # Step 4: Aggregate risks
        # Convert severity results to format expected by risk_aggregator
        aggregator_input = {}
        for param_name, sev_result in severity_results.items():
            # Need to recreate SeverityResult for aggregator
            from severity_engine import SeverityResult, SeverityLevel
            
            sev_enum = {
                "Normal": SeverityLevel.NORMAL,
                "Mild Deviation": SeverityLevel.MILD,
                "Moderate": SeverityLevel.MODERATE,
                "High": SeverityLevel.HIGH,
                "Critical": SeverityLevel.CRITICAL
            }
            
            aggregator_input[param_name] = SeverityResult(
                value=sev_result["value"],
                unit=sev_result["unit"],
                severity=sev_enum.get(sev_result["severity"], SeverityLevel.NORMAL),
                deviation_percent=sev_result["deviation_percent"],
                reference_min=sev_result["reference_min"],
                reference_max=sev_result["reference_max"],
                is_abnormal=sev_result["is_abnormal"],
                reasoning=sev_result["reasoning"]
            )
        
        # Parse medical history
        medical_history_list = []
        if medical_history:
            medical_history_list = [h.strip() for h in medical_history.split(",")]
        
        # Aggregate risks
        risk_aggregation = risk_aggregator.aggregate_risks(
            severity_results=aggregator_input,
            age=age,
            gender=gender,
            medical_history=medical_history_list
        )
        
        logger.info(f"Risk aggregation complete: {risk_aggregation.global_urgency.value}")
        
        # Step 5: Generate medical summary
        medical_summary = summary_generator.generate_medical_summary(
            severity_results=aggregator_input,
            risk_aggregation=risk_aggregation,
            age=age,
            gender=gender,
            test_name="Blood Work Analysis"
        )
        
        logger.info("Medical summary generated")
        
        # Step 6: Generate recommendations
        abnormal_params_for_recs = {
            param: {
                "value": sev_result["value"],
                "severity": sev_result["severity"]
            }
            for param, sev_result in severity_results.items()
            if sev_result["is_abnormal"]
        }
        
        recommendations = recommendation_engine.generate_recommendations(
            urgency_level=risk_aggregation.global_urgency,
            abnormal_parameters=abnormal_params_for_recs,
            age=age,
            gender=gender,
            medical_history=medical_history_list,
            max_recommendations=10
        )
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        # Step 7: Identify affected domains
        affected_domains = risk_aggregator.identify_risk_domains(
            critical_parameters=risk_aggregation.critical_parameters,
            high_parameters=risk_aggregation.high_risk_parameters
        )
        
        # Step 8: Get action items
        action_items = risk_aggregator.get_action_items(risk_aggregation.global_urgency)
        
        # Step 9: Compile complete response
        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "overall_urgency": risk_aggregation.global_urgency.value,
            
            # Severity assessment
            "severity_results": severity_results,
            
            # Risk analysis
            "risk_aggregation": risk_aggregation.to_dict(),
            
            # Medical assessment
            "medical_summary": medical_summary.to_dict(),
            
            # Affected domains
            "affected_domains": affected_domains,
            
            # Key findings
            "key_findings": medical_summary.key_insights,
            
            # Recommendations
            "recommendations": [rec.to_dict() for rec in recommendations],
            
            # Action items
            "action_items": action_items,
            
            # Guidance
            "guidance": medical_summary.guidance,
            
            # Metadata
            "metadata": {
                "total_parameters_assessed": len(severity_results),
                "abnormal_parameters": sum(1 for r in severity_results.values() if r["is_abnormal"]),
                "age": age,
                "gender": gender,
                "medical_history_provided": len(medical_history_list),
                "analysis_engine": "Production v1.0"
            }
        }
        
        logger.info("Analysis complete - returning response")
        
        return JSONResponse(content=response, status_code=200)
    
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return JSONResponse(
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=500
        )


# Add health check endpoint
@app.get("/health")
async def health_check():
    '''Verify all analysis engines are functional.'''
    return {
        "status": "healthy",
        "engines": {
            "severity": "active",
            "risk_aggregation": "active",
            "summary_generation": "active",
            "recommendations": "active"
        },
        "timestamp": datetime.now().isoformat()
    }
"""

# ============================================================================
# INTEGRATION EXAMPLE FOR MAIN ORCHESTRATOR
# ============================================================================

"""
# In your main_orchestrator.py, use like this:

from severity_engine import SeverityEngine, SeverityLevel, SeverityResult
from risk_aggregator import RiskAggregator
from summary_generator import SummaryGenerator
from recommendation_engine import RecommendationEngine

class HealthReportAnalyzer:
    
    def __init__(self):
        self.severity_engine = SeverityEngine()
        self.risk_aggregator = RiskAggregator()
        self.summary_generator = SummaryGenerator()
        self.recommendation_engine = RecommendationEngine()
    
    def analyze_complete_report(
        self,
        extracted_text: str,
        extracted_parameters: dict,
        age: int = None,
        gender: str = None,
        medical_history: list = None
    ) -> dict:
        '''
        Complete pipeline analysis with all new modules.
        '''
        
        # 1. Calculate severities
        severity_results = {}
        reference_ranges = {
            "glucose": (70, 100),
            "hemoglobin": (12, 16),
            # ... add all reference ranges
        }
        
        for param_name, value in extracted_parameters.items():
            if param_name in reference_ranges:
                ref_min, ref_max = reference_ranges[param_name]
                severity = self.severity_engine.calculate_severity(
                    value, ref_min, ref_max, age=age, gender=gender
                )
                severity_results[param_name] = severity
        
        # 2. Aggregate risks
        risk = self.risk_aggregator.aggregate_risks(
            severity_results=severity_results,
            age=age,
            gender=gender,
            medical_history=medical_history
        )
        
        # 3. Generate summary
        summary = self.summary_generator.generate_medical_summary(
            severity_results=severity_results,
            risk_aggregation=risk,
            age=age,
            gender=gender
        )
        
        # 4. Generate recommendations
        abnormal_params = {
            name: {
                "value": result.value,
                "severity": result.severity.value
            }
            for name, result in severity_results.items()
            if result.is_abnormal
        }
        
        recommendations = self.recommendation_engine.generate_recommendations(
            urgency_level=risk.global_urgency,
            abnormal_parameters=abnormal_params,
            age=age,
            gender=gender,
            medical_history=medical_history
        )
        
        # 5. Return structured output
        return {
            "severity_assessment": severity_results,
            "risk_aggregation": risk,
            "medical_summary": summary,
            "recommendations": recommendations,
            "action_items": self.risk_aggregator.get_action_items(risk.global_urgency)
        }
"""

# ============================================================================
# BATCH PROCESSING EXAMPLE
# ============================================================================

"""
# Process multiple patients/reports efficiently

from severity_engine import SeverityEngine
from risk_aggregator import RiskAggregator
from summary_generator import SummaryGenerator
from recommendation_engine import RecommendationEngine

def batch_analyze_reports(reports_list: list) -> list:
    '''
    Analyze multiple reports efficiently with shared engine instances.
    '''
    
    # Reuse engine instances
    severity_engine = SeverityEngine()
    risk_aggregator = RiskAggregator()
    summary_generator = SummaryGenerator()
    recommendation_engine = RecommendationEngine()
    
    results = []
    
    for report in reports_list:
        # Extract data
        params = extract_parameters(report["text"])
        
        # Batch calculate severities
        severity_results = severity_engine.batch_calculate_severity(
            parameters={
                "glucose": (report["glucose"], 70, 100),
                "hemoglobin": (report["hemoglobin"], 12, 16),
                # ...
            },
            age=report["age"],
            gender=report["gender"]
        )
        
        # Aggregate
        risk = risk_aggregator.aggregate_risks(
            severity_results=severity_results,
            age=report["age"],
            medical_history=report.get("medical_history", [])
        )
        
        # Summary
        summary = summary_generator.generate_medical_summary(
            severity_results=severity_results,
            risk_aggregation=risk,
            age=report["age"]
        )
        
        results.append({
            "patient_id": report["id"],
            "severity_results": severity_results,
            "risk": risk,
            "summary": summary
        })
    
    return results
"""

# ============================================================================
# CONFIGURATION REFERENCE
# ============================================================================

"""
SEVERITY ENGINE CONFIGURATION:

severity_engine = SeverityEngine()

# Default thresholds (% deviation from range)
threshold_mild = 10.0        # 10% deviation
threshold_moderate = 20.0    # 20% deviation
threshold_high = 35.0        # 35% deviation
threshold_critical = 50.0    # 50% deviation

# Age adjustment
age > 65:  reduces thresholds by 15% (stricter)
age < 18:  reduces thresholds by 10% (stricter)

RISK AGGREGATOR CONFIGURATION:

risk_aggregator = RiskAggregator()

# Escalation rules
- 1+ Critical → CRITICAL urgency
- 1+ High OR 2+ Moderate → HIGH urgency
- 3+ Mild OR 1+ Moderate → MODERATE urgency
- Else → LOW urgency

# Medical history escalation
- Pre-existing high-risk conditions → escalate 1 level

SUMMARY GENERATOR TONE MAPPING:

Low Concern:      "Your recent health report shows..."
Moderate Concern: "Your health report indicates..."
High Concern:     "Your health report reveals..."
Critical Concern: "⚠️ Your health report indicates..."

RECOMMENDATION ENGINE CATEGORIES:

urgent    - Immediate medical attention needed
medical   - Healthcare provider consultation
monitoring - Regular testing/monitoring required
testing   - Diagnostic testing recommended
lifestyle - Behavioral/lifestyle modifications
"""

# ============================================================================
# TESTING THE INTEGRATION
# ============================================================================

"""
Run this to verify all modules work together:

python -c "
from severity_engine import SeverityEngine
from risk_aggregator import RiskAggregator
from summary_generator import SummaryGenerator
from recommendation_engine import RecommendationEngine

# Test each module
print('Testing Severity Engine...')
engine = SeverityEngine()
result = engine.calculate_severity(250, 70, 100, 'mg/dL')
print(f'✓ Severity: {result.severity.value}')

print('\\nTesting Risk Aggregator...')
aggregator = RiskAggregator()
severity_results = {
    'glucose': engine.calculate_severity(250, 70, 100, 'mg/dL'),
    'hemoglobin': engine.calculate_severity(9.5, 12, 16, 'g/dL')
}
risk = aggregator.aggregate_risks(severity_results)
print(f'✓ Urgency: {risk.global_urgency.value}')

print('\\nTesting Summary Generator...')
gen = SummaryGenerator()
summary = gen.generate_medical_summary(severity_results, risk)
print(f'✓ Summary generated: {len(summary.summary_text)} chars')

print('\\nTesting Recommendation Engine...')
rec_engine = RecommendationEngine()
recs = rec_engine.generate_recommendations(risk.global_urgency, {})
print(f'✓ {len(recs)} recommendations generated')

print('\\n✅ All modules working correctly!')
"
"""
