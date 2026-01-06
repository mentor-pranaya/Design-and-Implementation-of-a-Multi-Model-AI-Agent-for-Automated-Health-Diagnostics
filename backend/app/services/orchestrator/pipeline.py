"""
Multi-Model Orchestrator
Coordinates the entire processing pipeline
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.input_parser import input_parser
from app.services.data_extraction import data_extractor
from app.services.validation import data_validator
from app.services.model_1_interpretation import parameter_interpreter

logger = logging.getLogger(__name__)

class ProcessingPipeline:
    """Orchestrate the multi-model processing pipeline"""
    
    def __init__(self):
        self.parser = input_parser
        self.extractor = data_extractor
        self.validator = data_validator
        self.interpreter = parameter_interpreter
    
    async def process_report(
        self,
        file_path: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a blood report through the complete pipeline
        
        Steps:
        1. Parse input file
        2. Extract parameters
        3. Validate and standardize
        4. Interpret parameters (Model 1)
        
        Returns: Complete analysis results
        """
        
        try:
            start_time = datetime.now()
            
            # Step 1: Parse input
            logger.info(f"Step 1: Parsing file {file_path}")
            parsed_data = await self.parser.parse_file(file_path)
            
            # Step 2: Extract parameters
            logger.info("Step 2: Extracting parameters")
            extracted_data = await self.extractor.extract(parsed_data)
            
            if not extracted_data.get("parameters"):
                raise ValueError("No parameters could be extracted from the report")
            
            # Step 3: Validate and standardize
            logger.info("Step 3: Validating and standardizing data")
            validated_data = await self.validator.validate(extracted_data)
            
            if not validated_data.get("validated_parameters"):
                raise ValueError("No valid parameters after validation")
            
            # Step 4: Interpret parameters (Model 1)
            logger.info("Step 4: Interpreting parameters")
            interpretation_results = await self.interpreter.interpret(
                validated_data, user_context
            )
            
            # Calculate processing metrics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Build complete result
            result = {
                "status": "completed",
                "processing_time_seconds": processing_time,
                "pipeline_stages": {
                    "parsing": {
                        "format": parsed_data.get("format"),
                        "metadata": parsed_data.get("metadata")
                    },
                    "extraction": {
                        "method": extracted_data.get("extraction_method"),
                        "total_extracted": extracted_data.get("total_extracted")
                    },
                    "validation": {
                        "total_validated": validated_data.get("total_validated"),
                        "total_invalid": validated_data.get("total_invalid"),
                        "issues": validated_data.get("validation_issues", [])
                    }
                },
                "extracted_parameters": extracted_data.get("parameters", []),
                "validated_parameters": validated_data.get("validated_parameters", []),
                "interpretations": interpretation_results.get("interpretations", []),
                "summary": interpretation_results.get("summary", {}),
                "critical_findings": interpretation_results.get("critical_findings", []),
                "abnormal_findings": interpretation_results.get("abnormal_findings", []),
                "user_context": interpretation_results.get("user_context", {}),
                "confidence_scores": {
                    "extraction": self._calculate_extraction_confidence(extracted_data),
                    "validation": self._calculate_validation_confidence(validated_data),
                    "interpretation": self._calculate_interpretation_confidence(interpretation_results)
                }
            }
            
            logger.info(f"Processing completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _calculate_extraction_confidence(self, extracted_data: Dict) -> float:
        """Calculate extraction confidence score"""
        parameters = extracted_data.get("parameters", [])
        
        if not parameters:
            return 0.0
        
        # Average confidence from extracted parameters
        confidences = [p.get("confidence", 0.5) for p in parameters]
        return round(sum(confidences) / len(confidences), 2)
    
    def _calculate_validation_confidence(self, validated_data: Dict) -> float:
        """Calculate validation confidence score"""
        total_validated = validated_data.get("total_validated", 0)
        total_invalid = validated_data.get("total_invalid", 0)
        total = total_validated + total_invalid
        
        if total == 0:
            return 0.0
        
        return round(total_validated / total, 2)
    
    def _calculate_interpretation_confidence(self, interpretation_results: Dict) -> float:
        """Calculate interpretation confidence score"""
        interpretations = interpretation_results.get("interpretations", [])
        
        if not interpretations:
            return 0.0
        
        # Average confidence from interpretations
        confidences = [i.get("confidence", 1.0) for i in interpretations]
        return round(sum(confidences) / len(confidences), 2)

# Global instance
processing_pipeline = ProcessingPipeline()
