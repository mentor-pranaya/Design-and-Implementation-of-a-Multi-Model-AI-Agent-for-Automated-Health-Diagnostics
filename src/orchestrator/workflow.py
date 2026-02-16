import traceback
from datetime import datetime

from src.input_parser.input_handler import read_input
from src.extraction.extractor import extract_parameter
from src.config.parameters import REQUIRED_PARAMETERS
from src.model_1.interpretation import interpret_value
from src.model_2.pattern_detector import detect_all_patterns
from src.model_2.risk_calculator import calculate_overall_risk
from src.model_3.contextual_analyzer import analyze_with_context
from src.synthesis.findings_engine import synthesize_findings
from src.synthesis.recommendation_generator import generate_recommendations


class HealthDiagnosticsOrchestrator:
    """
    Orchestrates the complete health diagnostics workflow
    Manages data flow between all models
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all internal state"""
        self.raw_data = None
        self.results = {}
        self.user_age = None
        self.user_gender = None
        self.contextual_analysis = None
        self.patterns = []
        self.risk_assessment = None
        self.synthesis = None
        self.recommendations = None
        self.errors = []
        self.warnings = []
        self.workflow_status = {
            "input_parsing": "pending",
            "extraction": "pending",
            "model_1": "pending",
            "model_3": "pending",
            "model_2_patterns": "pending",
            "model_2_risk": "pending",
            "synthesis": "pending",
            "recommendations": "pending"
        }
        self.start_time = None
        self.end_time = None
    
    def _log_error(self, stage, error_message, exception=None):
        """Log an error"""
        error = {
            "stage": stage,
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "exception": str(exception) if exception else None
        }
        self.errors.append(error)
        self.workflow_status[stage] = "failed"
    
    def _log_warning(self, stage, warning_message):
        """Log a warning"""
        warning = {
            "stage": stage,
            "message": warning_message,
            "timestamp": datetime.now().isoformat()
        }
        self.warnings.append(warning)
    
    def step_1_parse_input(self, file_path=None, file_content=None, file_type=None):
        """
        Step 1: Parse input file
        """
        try:
            if file_path:
                self.raw_data = read_input(file_path)
            elif file_content and file_type:
                # Handle uploaded file content
                self.raw_data = read_input(file_content, file_type=file_type)
            else:
                raise ValueError("No input provided")
            
            if self.raw_data is None:
                raise ValueError("Failed to read input file")
            
            self.workflow_status["input_parsing"] = "completed"
            return True
            
        except Exception as e:
            self._log_error("input_parsing", f"Failed to parse input: {str(e)}", e)
            return False
    
    def step_2_extract_parameters(self):
        """
        Step 2: Extract parameters from raw data
        """
        try:
            if self.raw_data is None:
                raise ValueError("No raw data available")
            
            self.results = {}
            
            # Unstructured input (OCR text)
            if isinstance(self.raw_data, str):
                for param_name, keywords in REQUIRED_PARAMETERS.items():
                    extracted = extract_parameter(self.raw_data, param_name, keywords)
                    self.results[param_name] = extracted.get(param_name) if extracted else None
            
            # Structured input (JSON dict)
            elif isinstance(self.raw_data, dict):
                for param_name in REQUIRED_PARAMETERS:
                    self.results[param_name] = self.raw_data.get(param_name)
            
            else:
                raise ValueError(f"Unsupported data type: {type(self.raw_data)}")
            
            # Extract Age with type safety
            age_data = self.results.get("Age")
            if age_data:
                age_value = age_data.get("value")
                if age_value is not None:
                    try:
                        self.user_age = int(float(age_value))
                    except (ValueError, TypeError):
                        self._log_warning("extraction", "Could not parse age value")
                        self.user_age = None
            
            # Extract Gender with type safety
            gender_data = self.results.get("Gender")
            if gender_data:
                gender_value = gender_data.get("value")
                if gender_value and isinstance(gender_value, str):
                    self.user_gender = gender_value.lower().strip()
                    if self.user_gender not in ["male", "female"]:
                        self._log_warning("extraction", f"Unknown gender value: {gender_value}")
                        self.user_gender = None
            
            # Count extracted parameters
            extracted_count = sum(1 for k, v in self.results.items() 
                                  if v is not None and k not in ["Age", "Gender"])
            
            if extracted_count == 0:
                self._log_warning("extraction", "No parameters were extracted from the report")
            
            self.workflow_status["extraction"] = "completed"
            return True
            
        except Exception as e:
            self._log_error("extraction", f"Failed to extract parameters: {str(e)}", e)
            return False
    
    def step_3_model_1_interpretation(self):
        """
        Step 3: Model 1 - Raw interpretation
        """
        try:
            for param_name, param_data in self.results.items():
                if param_name in ["Age", "Gender"]:
                    continue
                
                if param_data:
                    status = interpret_value(
                        value=param_data.get("value"),
                        reference_range=param_data.get("reference_range"),
                        param_name=param_name,
                        gender=self.user_gender,
                        age=self.user_age
                    )
                    param_data["status"] = status
            
            self.workflow_status["model_1"] = "completed"
            return True
            
        except Exception as e:
            self._log_error("model_1", f"Model 1 interpretation failed: {str(e)}", e)
            return False
    
    def step_4_model_3_contextual(self):
        """
        Step 4: Model 3 - Contextual analysis
        """
        try:
            self.contextual_analysis = analyze_with_context(
                results=self.results,
                age=self.user_age,
                gender=self.user_gender
            )
            
            self.workflow_status["model_3"] = "completed"
            return True
            
        except Exception as e:
            self._log_error("model_3", f"Model 3 contextual analysis failed: {str(e)}", e)
            return False
    
    def step_5_model_2_patterns(self):
        """
        Step 5: Model 2 - Pattern detection
        """
        try:
            self.patterns = detect_all_patterns(
                results=self.results,
                contextual_results=self.contextual_analysis["detailed_results"],
                gender=self.user_gender,
                age=self.user_age
            )
            
            self.workflow_status["model_2_patterns"] = "completed"
            return True
            
        except Exception as e:
            self._log_error("model_2_patterns", f"Pattern detection failed: {str(e)}", e)
            return False
    
    def step_6_model_2_risk(self):
        """
        Step 6: Model 2 - Risk assessment
        """
        try:
            self.risk_assessment = calculate_overall_risk(
                results=self.results,
                contextual_results=self.contextual_analysis["detailed_results"],
                gender=self.user_gender,
                age=self.user_age
            )
            
            self.workflow_status["model_2_risk"] = "completed"
            return True
            
        except Exception as e:
            self._log_error("model_2_risk", f"Risk assessment failed: {str(e)}", e)
            return False
    
    def step_7_synthesis(self):
        """
        Step 7: Synthesize findings
        """
        try:
            self.synthesis = synthesize_findings(
                results=self.results,
                patterns=self.patterns,
                risk_assessment=self.risk_assessment,
                contextual_analysis=self.contextual_analysis,
                age=self.user_age,
                gender=self.user_gender
            )
            
            self.workflow_status["synthesis"] = "completed"
            return True
            
        except Exception as e:
            self._log_error("synthesis", f"Findings synthesis failed: {str(e)}", e)
            return False
    
    def step_8_recommendations(self):
        """
        Step 8: Generate recommendations
        """
        try:
            self.recommendations = generate_recommendations(
                synthesis_result=self.synthesis,
                age=self.user_age,
                gender=self.user_gender
            )
            
            self.workflow_status["recommendations"] = "completed"
            return True
            
        except Exception as e:
            self._log_error("recommendations", f"Recommendation generation failed: {str(e)}", e)
            return False
    
    def run_full_workflow(self, file_path=None, file_content=None, file_type=None):
        """
        Run the complete end-to-end workflow
        
        Returns:
            dict: Complete analysis results
        """
        self.reset()
        self.start_time = datetime.now()
        
        # Execute all steps
        steps = [
            ("Input Parsing", lambda: self.step_1_parse_input(file_path, file_content, file_type)),
            ("Parameter Extraction", self.step_2_extract_parameters),
            ("Model 1 - Interpretation", self.step_3_model_1_interpretation),
            ("Model 3 - Contextual Analysis", self.step_4_model_3_contextual),
            ("Model 2 - Pattern Detection", self.step_5_model_2_patterns),
            ("Model 2 - Risk Assessment", self.step_6_model_2_risk),
            ("Findings Synthesis", self.step_7_synthesis),
            ("Recommendation Generation", self.step_8_recommendations)
        ]
        
        for step_name, step_func in steps:
            success = step_func()
            if not success:
                # Continue with remaining steps if possible
                pass
        
        self.end_time = datetime.now()
        
        return self.get_results()
    
    def get_results(self):
        """
        Get complete results
        """
        # Calculate processing time
        processing_time = None
        if self.start_time and self.end_time:
            processing_time = (self.end_time - self.start_time).total_seconds()
        
        # Determine overall success
        failed_steps = [k for k, v in self.workflow_status.items() if v == "failed"]
        success = len(failed_steps) == 0
        
        return {
            "success": success,
            "processing_time_seconds": processing_time,
            "workflow_status": self.workflow_status,
            "patient_info": {
                "age": self.user_age,
                "gender": self.user_gender,
                "age_group": self.synthesis.get("age_group") if self.synthesis else None
            },
            "parameters": self.results,
            "contextual_analysis": self.contextual_analysis,
            "patterns": self.patterns,
            "risk_assessment": self.risk_assessment,
            "synthesis": self.synthesis,
            "recommendations": self.recommendations,
            "errors": self.errors,
            "warnings": self.warnings
        }


def run_diagnostics(file_path=None, file_content=None, file_type=None):
    """
    Convenience function to run diagnostics
    """
    orchestrator = HealthDiagnosticsOrchestrator()
    return orchestrator.run_full_workflow(file_path, file_content, file_type)