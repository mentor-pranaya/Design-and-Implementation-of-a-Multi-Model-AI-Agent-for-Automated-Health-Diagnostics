"""
Multi-Model Orchestrator - Phase 3
Manages the flow of data between different components and AI models.

This is the central coordination component required by the organization's
project plan. It ensures models are called in the correct sequence and
data flows properly through the entire pipeline.

Architecture:
    Input → Extraction → Validation → Model 1 → Model 2 → Model 3 → 
    Synthesis → Recommendations → Report

Design Philosophy:
- Single point of coordination for all models
- Clear separation of concerns
- Error handling at each stage
- Logging and monitoring support
- Extensible for future models
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import json


class MultiModelOrchestrator:
    """
    Central orchestrator for the multi-model AI pipeline.
    
    Responsibilities:
    1. Coordinate data flow between all components
    2. Ensure models are called in correct sequence
    3. Handle errors and edge cases gracefully
    4. Provide logging and monitoring hooks
    5. Manage model dependencies and context
    
    This component fulfills the organization's requirement for:
    "Multi-Model Orchestrator: Manages the flow of data between the 
    different components and AI models, ensuring they are called in 
    the correct sequence."
    """
    
    def __init__(
        self,
        enable_model3: bool = True,
        enable_risk_scoring: bool = True,
        verbose: bool = False
    ):
        """
        Initialize the multi-model orchestrator.
        
        Args:
            enable_model3: Whether to use contextual analysis (Model 3)
            enable_risk_scoring: Whether to calculate risk scores
            verbose: Enable detailed logging
        """
        self.enable_model3 = enable_model3
        self.enable_risk_scoring = enable_risk_scoring
        self.verbose = verbose
        
        # Initialize components (lazy loading)
        self._extractor = None
        self._validator = None
        self._model1 = None
        self._model2 = None
        self._model3 = None
        self._evaluator = None
        self._risk_scorer = None
        self._recommender = None
        self._report_generator = None
        
        # Execution state
        self.execution_log = []
        self.errors = []
        
        if self.verbose:
            print("✓ Multi-Model Orchestrator initialized")
            print(f"  Model 3 (Contextual): {'Enabled' if enable_model3 else 'Disabled'}")
            print(f"  Risk Scoring: {'Enabled' if enable_risk_scoring else 'Disabled'}")
    
    # =========================================================================
    # PUBLIC API - Main Orchestration Method
    # =========================================================================
    
    def process_blood_report(
        self,
        report_path: str,
        patient_context: Optional[Dict[str, Any]] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Process a blood report through the complete multi-model pipeline.
        
        This is the main entry point that orchestrates all models in sequence.
        
        Workflow:
        1. Extract data from report (OCR/parsing)
        2. Validate and standardize data
        3. Model 1: Parameter interpretation
        4. Model 2: Pattern recognition
        5. Model 3: Contextual analysis (if enabled and context provided)
        6. Synthesize findings
        7. Generate recommendations
        8. Format report
        
        Args:
            report_path: Path to blood report (PDF, image, or JSON)
            patient_context: Optional patient information
                {
                    "age": 45,
                    "sex": "male",
                    "known_conditions": ["diabetes"],
                    "lifestyle": {"smoker": True}
                }
            output_format: Output format ("json", "text", "pdf")
        
        Returns:
            Complete analysis results including findings and recommendations
        """
        self._log("Starting multi-model pipeline")
        
        try:
            # Stage 1: Data Extraction
            self._log("Stage 1: Data Extraction")
            extracted_data = self._extract_data(report_path)
            
            # Stage 2: Data Validation
            self._log("Stage 2: Data Validation")
            validated_data = self._validate_data(extracted_data)
            
            # Stage 3: Model 1 - Parameter Interpretation
            self._log("Stage 3: Model 1 - Parameter Interpretation")
            parameter_evaluations = self._run_model1(validated_data, patient_context)
            
            # Stage 4: Model 2 - Pattern Recognition
            self._log("Stage 4: Model 2 - Pattern Recognition")
            detected_patterns = self._run_model2(parameter_evaluations)
            
            # Stage 5: Model 3 - Contextual Analysis (Optional)
            if self.enable_model3 and patient_context:
                self._log("Stage 5: Model 3 - Contextual Analysis")
                contextualized_patterns = self._run_model3(
                    detected_patterns,
                    parameter_evaluations,
                    patient_context
                )
            else:
                self._log("Stage 5: Model 3 - Skipped (disabled or no context)")
                contextualized_patterns = detected_patterns
            
            # Stage 6: Risk Scoring (Optional)
            risk_scores = None
            if self.enable_risk_scoring:
                self._log("Stage 6: Risk Scoring")
                risk_scores = self._calculate_risk_scores(
                    parameter_evaluations,
                    contextualized_patterns,
                    patient_context
                )
            
            # Stage 7: Synthesize Findings
            self._log("Stage 7: Synthesize Findings")
            synthesized_findings = self._synthesize_findings(
                parameter_evaluations,
                contextualized_patterns,
                risk_scores
            )
            
            # Stage 8: Generate Recommendations
            self._log("Stage 8: Generate Recommendations")
            recommendations = self._generate_recommendations(
                contextualized_patterns,
                synthesized_findings
            )
            
            # Stage 9: Format Report
            self._log("Stage 9: Format Report")
            final_report = self._format_report(
                synthesized_findings,
                recommendations,
                output_format
            )
            
            self._log("✓ Pipeline completed successfully")
            
            return {
                "status": "success",
                "report": final_report,
                "metadata": {
                    "models_used": self._get_models_used(),
                    "execution_log": self.execution_log,
                    "patient_context_provided": patient_context is not None
                }
            }
            
        except Exception as e:
            self._log_error(f"Pipeline failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "execution_log": self.execution_log,
                "errors": self.errors
            }
    
    # =========================================================================
    # STAGE IMPLEMENTATIONS
    # =========================================================================
    
    def _extract_data(self, report_path: str) -> Dict[str, Any]:
        """
        Stage 1: Extract data from blood report.
        
        Handles PDF, image, and JSON formats.
        """
        # TODO: Implement actual extraction logic
        # For now, return placeholder
        self._log("  Extracting parameters from report")
        
        # This would call your Phase 1 OCR pipeline
        # from core_phase1.ocr import extract_from_pdf
        # extracted = extract_from_pdf(report_path)
        
        return {
            "Hemoglobin": {"value": 14.5, "unit": "g/dL"},
            "Glucose": {"value": 110, "unit": "mg/dL"},
            "Creatinine": {"value": 1.1, "unit": "mg/dL"}
        }
    
    def _validate_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 2: Validate and standardize extracted data.
        
        Uses Phase 1 validator.
        """
        self._log("  Validating extracted parameters")
        
        # This would call your validator
        # from core_phase1.validation.validator import validate_parameters
        # validated = validate_parameters(extracted_data)
        
        return extracted_data
    
    def _run_model1(
        self,
        validated_data: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Stage 3: Model 1 - Parameter Interpretation.
        
        Compares individual parameters against reference ranges.
        """
        self._log("  Classifying parameters against reference ranges")
        
        # This would call your Phase 3 evaluation engine
        # from core_phase3.knowledge_base.reference_manager import ReferenceRangeManager
        # manager = ReferenceRangeManager()
        # evaluations = []
        # for param, details in validated_data.items():
        #     eval_result = manager.evaluate_value(
        #         param, 
        #         details['value'],
        #         sex=patient_context.get('sex') if patient_context else None
        #     )
        #     evaluations.append(eval_result)
        
        return []
    
    def _run_model2(
        self,
        parameter_evaluations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Stage 4: Model 2 - Pattern Recognition.
        
        Identifies clinical patterns from parameter combinations.
        """
        self._log("  Detecting clinical patterns")
        
        # This would call your Phase 2 pattern detection
        # from core_phase2.interpreter.model2_patterns import (
        #     diabetes_indicator,
        #     metabolic_syndrome_indicators,
        #     kidney_function_assessment
        # )
        
        return []
    
    def _run_model3(
        self,
        detected_patterns: List[Dict[str, Any]],
        parameter_evaluations: List[Dict[str, Any]],
        patient_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Stage 5: Model 3 - Contextual Analysis.
        
        Refines interpretations based on patient context.
        """
        self._log("  Applying contextual refinements")
        
        # This would apply contextual adjustments
        # Adjust risk scores based on age, sex, lifestyle, medical history
        
        return detected_patterns
    
    def _calculate_risk_scores(
        self,
        parameter_evaluations: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        patient_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stage 6: Calculate risk scores.
        
        Uses risk scoring engines.
        """
        self._log("  Calculating risk scores")
        
        # This would call your risk scoring engines
        # from core_phase3.risk_scoring_engine import calculate_cardiovascular_risk
        # from core_phase3.health_risk_engine import ComprehensiveHealthRiskEngine
        
        return {}
    
    def _synthesize_findings(
        self,
        parameter_evaluations: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        risk_scores: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stage 7: Synthesize findings from all models.
        
        Aggregates results into coherent summary.
        """
        self._log("  Synthesizing findings")
        
        return {
            "summary": "Analysis complete",
            "abnormal_parameters": [],
            "detected_patterns": patterns,
            "risk_assessment": risk_scores
        }
    
    def _generate_recommendations(
        self,
        patterns: List[Dict[str, Any]],
        findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage 8: Generate personalized recommendations.
        
        Uses recommendation engine.
        """
        self._log("  Generating recommendations")
        
        # This would call your recommendation engine
        # from core_phase3.recommendations.recommender import RecommendationEngine
        # engine = RecommendationEngine()
        # recommendations = engine.generate_recommendations(patterns)
        
        return {}
    
    def _format_report(
        self,
        findings: Dict[str, Any],
        recommendations: Dict[str, Any],
        output_format: str
    ) -> Any:
        """
        Stage 9: Format final report.
        
        Generates user-friendly output.
        """
        self._log(f"  Formatting report as {output_format}")
        
        if output_format == "json":
            return {
                "findings": findings,
                "recommendations": recommendations
            }
        elif output_format == "text":
            # Generate text report
            return "Text report placeholder"
        elif output_format == "pdf":
            # Generate PDF report
            return "PDF report placeholder"
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _log(self, message: str):
        """Log execution step."""
        self.execution_log.append(message)
        if self.verbose:
            print(message)
    
    def _log_error(self, error: str):
        """Log error."""
        self.errors.append(error)
        self._log(f"ERROR: {error}")
    
    def _get_models_used(self) -> List[str]:
        """Get list of models used in this execution."""
        models = ["Model 1 (Parameter Interpretation)", "Model 2 (Pattern Recognition)"]
        if self.enable_model3:
            models.append("Model 3 (Contextual Analysis)")
        if self.enable_risk_scoring:
            models.append("Risk Scoring Engine")
        return models
    
    # =========================================================================
    # CONFIGURATION METHODS
    # =========================================================================
    
    def enable_contextual_analysis(self, enable: bool = True):
        """Enable or disable Model 3 (Contextual Analysis)."""
        self.enable_model3 = enable
        self._log(f"Model 3 (Contextual Analysis): {'Enabled' if enable else 'Disabled'}")
    
    def enable_risk_scoring_engine(self, enable: bool = True):
        """Enable or disable risk scoring."""
        self.enable_risk_scoring = enable
        self._log(f"Risk Scoring: {'Enabled' if enable else 'Disabled'}")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline configuration and status."""
        return {
            "model3_enabled": self.enable_model3,
            "risk_scoring_enabled": self.enable_risk_scoring,
            "verbose": self.verbose,
            "execution_count": len(self.execution_log),
            "error_count": len(self.errors)
        }


# =========================================================================
# CONVENIENCE FUNCTIONS
# =========================================================================

def process_report(
    report_path: str,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None,
    known_conditions: Optional[List[str]] = None,
    lifestyle: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to process a blood report.
    
    Args:
        report_path: Path to blood report file
        patient_age: Patient age (optional)
        patient_sex: Patient sex ("male" or "female", optional)
        known_conditions: List of known medical conditions (optional)
        lifestyle: Lifestyle factors (optional)
    
    Returns:
        Complete analysis results
    """
    # Build patient context if any information provided
    patient_context = None
    if any([patient_age, patient_sex, known_conditions, lifestyle]):
        patient_context = {}
        if patient_age:
            patient_context["age"] = patient_age
        if patient_sex:
            patient_context["sex"] = patient_sex
        if known_conditions:
            patient_context["known_conditions"] = known_conditions
        if lifestyle:
            patient_context["lifestyle"] = lifestyle
    
    # Create orchestrator and process
    orchestrator = MultiModelOrchestrator(
        enable_model3=patient_context is not None,
        enable_risk_scoring=True,
        verbose=True
    )
    
    return orchestrator.process_blood_report(
        report_path,
        patient_context=patient_context
    )


if __name__ == "__main__":
    # Example usage
    print("="*70)
    print("Multi-Model Orchestrator - Example Usage")
    print("="*70)
    
    # Example 1: Basic processing without context
    print("\nExample 1: Basic Processing")
    print("-"*70)
    orchestrator = MultiModelOrchestrator(verbose=True)
    result = orchestrator.process_blood_report("sample_report.pdf")
    print(f"\nStatus: {result['status']}")
    print(f"Models used: {result['metadata']['models_used']}")
    
    # Example 2: Processing with patient context
    print("\n\nExample 2: Processing with Patient Context")
    print("-"*70)
    patient_context = {
        "age": 55,
        "sex": "male",
        "known_conditions": ["hypertension", "diabetes"],
        "lifestyle": {
            "smoker": True,
            "exercise_level": "low"
        }
    }
    
    result = process_report(
        "sample_report.pdf",
        patient_age=55,
        patient_sex="male",
        known_conditions=["hypertension", "diabetes"],
        lifestyle={"smoker": True, "exercise_level": "low"}
    )
    
    print(f"\nStatus: {result['status']}")
    print(f"Context provided: {result['metadata']['patient_context_provided']}")
    
    # Example 3: Get pipeline status
    print("\n\nExample 3: Pipeline Status")
    print("-"*70)
    status = orchestrator.get_pipeline_status()
    print(json.dumps(status, indent=2))
