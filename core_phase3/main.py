"""
Phase 3: Recommendation Engine Main Module
Orchestrates the complete Phase 3 pipeline with evidence-based evaluation.

Architecture (Multi-Model AI Agent):
1. Phase 3A: Reference-Based Evaluation (Model 1 - Evidence Foundation)
   - Input: Extracted parameters from Phase 2
   - Process: Classify against authoritative reference ranges
   - Output: Clinical status (Low/Normal/High/Critical) with severity

2. Phase 3B: Pattern Recognition (Model 2 - Contextual Risk Assessment)
   - Input: Evaluation results + extracted parameters
   - Process: Detect multi-parameter risk patterns
   - Output: Risk patterns (e.g., Anemia Indicator, Diabetes Risk)

3. Phase 3D: Contextual Refinement (Model 3 - Personalization Layer)
   - Input: Evaluations + Patterns + Patient Context
   - Process: Refine interpretations based on age, gender, history, lifestyle
   - Output: Personalized risk scores with contextual modifiers

4. Phase 3E: Quantified Risk Scoring (NEW - Clinical Decision Support)
   - Input: Evaluations + Patient Context
   - Process: Calculate structured, quantified risk scores (CV, diabetes, CKD)
   - Output: 10-year risk percentages, risk categories, criteria triggers

5. Phase 3C: Recommendation Generation (Synthesized Guidance)
   - Input: Contextually-refined evaluations + patterns + risk scores
   - Process: Multi-model reasoning combining all signals
   - Output: Personalized evidence-based lifestyle recommendations

Design Philosophy:
- Evidence-based: All evaluations grounded in reference ranges
- Multi-signal: Combines evaluation + pattern recognition
- Clinically sound: Mimics real diagnostic workflow
- Auditable: Clear decision trail from data → recommendations
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from evaluation.evaluator import ParameterEvaluator
from contextual_model import ContextualRefiner
from health_risk_engine import ComprehensiveHealthRiskEngine
from recommendations.recommender import (
    RecommendationEngine,
    SafetyValidator,
    format_recommendations_for_display
)
from recommendations.diet import DietRecommendationModule
from recommendations.exercise import ExerciseRecommendationModule
from recommendations.lifestyle import LifestyleRecommendationModule


class Phase3RecommendationPipeline:
    """
    Orchestrates Phase 3: Complete Evaluation & Recommendation Pipeline
    
    Pipeline Flow:
    Extracted Parameters (Phase 2)
      ↓
    Phase 3A: Reference-Based Evaluation
      ↓
    Phase 3B: Pattern Recognition (enhanced by evaluation)
      ↓
    Phase 3C: Multi-Model Recommendation Synthesis
      ↓
    Final Comprehensive Report
    
    This implements a multi-model AI agent that:
    - Evaluates against authoritative references
    - Detects complex multi-parameter patterns
    - Synthesizes evidence-based recommendations
    """
    
    def __init__(self):
        """Initialize all Phase 3 components."""
        print("\n" + "="*70)
        print("Initializing Phase 3: Evaluation & Recommendation Pipeline")
        print("="*70)
        
        self.evaluator = ParameterEvaluator()
        self.engine = RecommendationEngine()
        self.diet_module = DietRecommendationModule()
        self.exercise_module = ExerciseRecommendationModule()
        self.lifestyle_module = LifestyleRecommendationModule()
        self.validator = SafetyValidator()
        
        print("✓ All Phase 3 modules initialized successfully\n")
    
    def process_extracted_parameters(
        self,
        extracted_parameters: List[Dict[str, Any]],
        patient_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Complete Phase 3 pipeline: Evaluate → Detect Patterns → Generate Recommendations.
        
        This is the main entry point that orchestrates the full pipeline.
        
        Args:
            extracted_parameters: Parameters from Phase 2 extraction
                Format: [{"parameter": "Hemoglobin", "value": 12.5, "unit": "g/dL"}, ...]
            patient_info: Optional patient demographics
                Format: {"sex": "female", "age": 45}
        
        Returns:
            Comprehensive report with evaluations, patterns, and recommendations
        """
        print("Starting Phase 3 Pipeline...")
        print("-" * 70)
        
        # PHASE 3A: Reference-Based Evaluation
        print("\n[Phase 3A] Reference-Based Evaluation...")
        evaluation_results = self.evaluator.evaluate_parameters(
            extracted_parameters, 
            patient_info
        )
        print(f"✓ Evaluated {evaluation_results['total_parameters_evaluated']} parameters")
        print(f"  Abnormal findings: {len(evaluation_results['abnormal_findings'])}")
        print(f"  Critical findings: {len(evaluation_results['critical_findings'])}")
        
        # PHASE 3B: Pattern Recognition (enhanced by evaluation flags)
        print("\n[Phase 3B] Pattern Recognition...")
        pattern_flags = evaluation_results.get('flags_for_pattern_recognition', [])
        patterns = self._convert_flags_to_patterns(pattern_flags)
        print(f"✓ Detected {len(patterns)} clinical patterns")
        
        # PHASE 3D: Contextual Refinement (Model 3 - Personalization)
        print("\n[Phase 3D] Applying Contextual Refinements...")
        if patient_info:
            refiner = ContextualRefiner(patient_info)
            refined_results = refiner.refine(
                evaluated_parameters=evaluation_results,
                detected_patterns={'patterns': patterns}
            )
            # Extract refined patterns
            refined_patterns = refined_results['detected_patterns'].get('patterns', patterns)
            contextual_modifiers = refined_results.get('contextual_modifiers', [])
            personalization_summary = refined_results.get('personalization_summary', {})
            print(f"✓ Applied contextual refinements")
        else:
            refined_patterns = patterns
            contextual_modifiers = []
            personalization_summary = {}
            print("⚠ No patient context provided - skipping personalization")
        
        # PHASE 3E: Quantified Risk Scoring (NEW LAYER)
        print("\n[Phase 3E] Calculating Quantified Risk Scores...")
        health_risk = None
        if patient_info:
            try:
                risk_engine = ComprehensiveHealthRiskEngine(
                    patient_info=patient_info,
                    parameter_evaluations=evaluation_results.get("evaluations", []),
                    detected_patterns=patterns
                )
                health_risk = risk_engine.calculate()
                print(f"✓ Health Risk Score: {health_risk['total_score']} ({health_risk['risk_category']})")
            except Exception as e:
                print(f"⚠ Could not calculate health risk: {e}")
                health_risk = {"error": str(e)}
        else:
            print("⚠ No patient context - skipping risk scoring")
        
        # PHASE 3C: Multi-Model Recommendation Synthesis
        print("\n[Phase 3C] Generating Evidence-Based Recommendations...")
        base_recommendations = self.engine.generate_recommendations(
            patterns=refined_patterns,
            evaluations=evaluation_results
        )
        pattern_count = base_recommendations.get('detected_patterns_count', len(refined_patterns))
        print(f"✓ Generated recommendations for {pattern_count} conditions")
        
        # Enhance with specialized modules
        enhanced_recommendations = self._enhance_recommendations(
            base_recommendations, 
            patterns
        )
        
        # Safety validation
        validation = self.validator.validate_recommendations(enhanced_recommendations)
        
        # Create comprehensive final report
        final_report = {
            "phase": "Phase 3: Complete Evaluation & Recommendation Pipeline",
            "timestamp": self._get_timestamp(),
            "patient_info": patient_info or {'sex': 'not_specified', 'age': 'not_specified'},
            
            # Phase 3A Output
            "phase_3a_evaluation": evaluation_results,
            
            # Phase 3B Output
            "phase_3b_patterns": patterns,
            
            # Phase 3D Output (Contextual Refinement)
            "phase_3d_contextual_refinement": {
                "refined_patterns": refined_patterns,
                "contextual_modifiers": contextual_modifiers,
                "personalization_summary": personalization_summary
            },
            
            # Phase 3E Output (Quantified Risk Scoring) - Comprehensive Health Risk
            "phase_3e_risk_scoring": health_risk,
            
            # Phase 3C Output
            "phase_3c_recommendations": enhanced_recommendations,
            
            # Validation
            "safety_validation": validation,
            
            # Formatted output for display
            "formatted_output": format_recommendations_for_display(enhanced_recommendations)
        }
        
        print("\n" + "="*70)
        print("✓ Phase 3 Pipeline Complete")
        print("="*70 + "\n")
        
        return final_report
    
    def _convert_flags_to_patterns(
        self, 
        flags: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert evaluation flags to pattern format.
        
        Bridges Phase 3A (evaluation) → Phase 3B (patterns).
        
        Args:
            flags: Pattern flags from evaluation engine
        
        Returns:
            List of patterns in expected format
        """
        patterns = []
        for flag in flags:
            patterns.append({
                "pattern": flag['pattern_type'],
                "severity": flag.get('severity', 'Moderate'),
                "confidence": flag.get('confidence', 'moderate'),
                "triggered_by": flag.get('triggered_by', [])
            })
        return patterns
    
    def process_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Legacy method: Process patterns directly (backward compatibility).
        
        This method is maintained for backward compatibility with Phase 2 integration.
        New code should use process_extracted_parameters() instead.
        
        Args:
            patterns: List of detected patterns from Phase 2
                     Example: [{"pattern": "Anemia Indicator", "severity": "Mild"}]
        
        Returns:
            Recommendation report (without evaluation layer)
        """
        print("\n⚠️  Using legacy pattern-only mode (no reference evaluation)")
        print("   Consider migrating to process_extracted_parameters() for full evaluation\n")
        
        # Generate base recommendations from engine (patterns only)
        base_recommendations = self.engine.generate_recommendations(patterns=patterns)
        
        # Enhance with specialized module details
        enhanced_recommendations = self._enhance_recommendations(base_recommendations, patterns)
        
        # Validate for safety and ethics
        validation = self.validator.validate_recommendations(enhanced_recommendations)
        
        # Create final report
        final_report = {
            "phase": "Phase 3: Recommendation Engine (Pattern-Only Mode)",
            "timestamp": self._get_timestamp(),
            "input_patterns": patterns,
            "base_recommendations": base_recommendations,
            "enhanced_recommendations": enhanced_recommendations,
            "safety_validation": validation,
            "formatted_output": format_recommendations_for_display(enhanced_recommendations)
        }
        
        return final_report
    
    def _enhance_recommendations(self, base_recs: Dict[str, Any], patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enhance base recommendations with specialized module details.
        
        Args:
            base_recs: Base recommendations from RecommendationEngine
            patterns: Original detected patterns
            
        Returns:
            Enhanced recommendations with specialized guidance
        """
        enhanced = base_recs.copy()
        enhanced["detailed_guidance"] = {}
        
        for pattern in patterns:
            condition = pattern.get("pattern")
            severity = pattern.get("severity", "Moderate")
            
            # Get specialized guidance for this condition
            specialized = {
                "diet_details": self.diet_module.get_diet_recommendations(condition),
                "diet_tips": self.diet_module.get_meal_planning_tips([condition]),
                "exercise_plan": self.exercise_module.get_exercise_recommendations(condition, severity),
                "lifestyle_guidance": self.lifestyle_module.get_lifestyle_recommendations(condition)
            }
            
            enhanced["detailed_guidance"][condition] = specialized
        
        return enhanced
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


def generate_recommendations_from_phase2_output(phase2_output_file: str) -> str:
    """
    Generate recommendations from Phase 2 output file.
    
    Args:
        phase2_output_file: Path to Phase 2 output JSON file
        
    Returns:
        Formatted recommendations text
    """
    try:
        # Load Phase 2 output
        with open(phase2_output_file, 'r', encoding='utf-8') as f:
            phase2_data = json.load(f)
        
        # Extract patterns from Phase 2 output
        patterns = phase2_data.get("patterns", [])
        
        # Generate recommendations
        pipeline = Phase3RecommendationPipeline()
        report = pipeline.process_patterns(patterns)
        
        return report["formatted_output"]
    
    except FileNotFoundError:
        return f"Error: Phase 2 output file not found at {phase2_output_file}"
    except Exception as e:
        return f"Error processing Phase 2 output: {str(e)}"


def main():
    """
    Main entry point for Phase 3.
    Demonstrates the complete evaluation and recommendation pipeline.
    """
    print("\n" + "="*70)
    print("PHASE 3: EVALUATION & RECOMMENDATION PIPELINE - DEMONSTRATION")
    print("="*70)
    print("\nThis module implements a multi-model AI agent that:")
    print("  1. Evaluates parameters against authoritative reference ranges")
    print("  2. Detects complex multi-parameter risk patterns")
    print("  3. Generates evidence-based lifestyle recommendations\n")
    
    pipeline = Phase3RecommendationPipeline()
    
    # Example 1: Complete pipeline with extracted parameters
    print("\n" + "─"*70)
    print("EXAMPLE 1: Complete Pipeline (Evaluation → Pattern → Recommendation)")
    print("─"*70)
    
    sample_parameters = [
        {"parameter": "Hemoglobin", "value": 10.8, "unit": "g/dL"},
        {"parameter": "Glucose", "value": 128, "unit": "mg/dL"},
        {"parameter": "HbA1c", "value": 6.2, "unit": "%"},
        {"parameter": "LDL", "value": 165, "unit": "mg/dL"},
        {"parameter": "HDL", "value": 38, "unit": "mg/dL"},
    ]
    
    patient_info = {"sex": "male", "age": 45}
    
    report_1 = pipeline.process_extracted_parameters(sample_parameters, patient_info)
    print(report_1["formatted_output"])
    
    # Example 2: Legacy pattern-only mode
    print("\n" + "─"*70)
    print("EXAMPLE 2: Legacy Pattern-Only Mode (Backward Compatibility)")
    print("─"*70)
    
    legacy_patterns = [
        {"pattern": "High Blood Pressure", "severity": "Moderate"}
    ]
    
    report_2 = pipeline.process_patterns(legacy_patterns)
    print(report_2["formatted_output"])
    
    # Display available conditions
    print("\n" + "─"*70)
    print("AVAILABLE CONDITIONS IN KNOWLEDGE BASE:")
    print("─"*70)
    conditions = pipeline.engine.get_available_conditions()
    for i, condition in enumerate(conditions, 1):
        print(f"{i:2d}. {condition}")
    
    print("\n" + "="*70)
    print("END OF DEMONSTRATION")
    print("="*70)
    print("\n💡 Key Architecture Points for Viva:")
    print("   • Evaluation determines clinical status (reference-based)")
    print("   • Patterns provide contextual risk signals")
    print("   • Recommendations synthesize both (multi-model reasoning)")
    print("   • All decisions auditable and evidence-backed")
    print("="*70 + "\n")


if __name__ == "__main__":
    # You can also import and use this module in Phase 2's main.py
    # Example:
    # from core_phase3.main import Phase3RecommendationPipeline
    # pipeline = Phase3RecommendationPipeline()
    # recommendations = pipeline.process_patterns(patterns_from_phase2)
    
    main()
