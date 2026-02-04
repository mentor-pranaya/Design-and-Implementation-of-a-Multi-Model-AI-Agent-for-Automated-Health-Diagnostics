"""
Recommendation Engine - Phase 3
Converts detected medical patterns into safe, evidence-based lifestyle recommendations.
Knowledge-driven approach using external clinical guidelines.

SAFETY DISCLAIMER:
This recommendation engine provides general lifestyle guidance based on detected 
medical patterns and clinical guidelines. It does NOT replace professional medical advice. 
Users should always consult with healthcare providers for personalized medical recommendations.
"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path


class RecommendationEngine:
    """
    Core recommendation engine that converts medical patterns into actionable recommendations.
    
    Workflow:
    1. Load medical guidelines from JSON
    2. Match detected patterns to guidelines
    3. Generate recommendations for diet, exercise, and follow-up
    4. Return structured recommendation output
    """
    
    def __init__(self, guidelines_path: str = None):
        """
        Initialize the recommendation engine.
        
        Args:
            guidelines_path: Path to medical_guidelines.json. 
                           If None, uses default path relative to script location.
        """
        if guidelines_path is None:
            # Get the directory where this script is located
            script_dir = Path(__file__).parent.parent
            guidelines_path = os.path.join(script_dir, 'knowledge_base', 'medical_guidelines.json')
        
        self.guidelines_path = guidelines_path
        self.medical_guidelines = self._load_guidelines()
    
    def _load_guidelines(self) -> Dict[str, Any]:
        """
        Load medical guidelines from JSON file.
        
        Returns:
            Dictionary containing medical guidelines for various conditions.
            
        Raises:
            FileNotFoundError: If guidelines file not found.
            json.JSONDecodeError: If JSON is invalid.
        """
        try:
            with open(self.guidelines_path, 'r', encoding='utf-8') as f:
                guidelines = json.load(f)
            print(f"✓ Loaded {len(guidelines)} medical condition guidelines")
            return guidelines
        except FileNotFoundError:
            raise FileNotFoundError(f"Medical guidelines not found at {self.guidelines_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in guidelines: {e}", e.doc, e.pos)
    
    def generate_recommendations(
        self, 
        patterns: List[Dict[str, Any]] = None,
        evaluations: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate recommendations based on evaluation results AND detected patterns.
        
        This method implements multi-model reasoning:
        - Evaluations provide reference-based clinical status (Low/Normal/High)
        - Patterns provide contextual risk signals
        - Recommendations synthesize both for evidence-based guidance
        
        Args:
            patterns: List of detected patterns from Phase 3B (Pattern Recognition)
                     Example: [{"pattern": "Anemia Indicator", "severity": "Mild"}]
            evaluations: Evaluation results from Phase 3A (Reference-Based Evaluation)
                        Contains evaluated parameters with status and severity
        
        Returns:
            Dictionary containing structured recommendations synthesizing both inputs.
        """
        # Backward compatibility: accept patterns only
        if patterns is None:
            patterns = []
        
        # Handle case where no abnormalities detected
        if not patterns and (evaluations is None or not evaluations.get('abnormal_findings', [])):
            return {
                "status": "success",
                "message": "No abnormalities detected. General wellness recommendations apply.",
                "recommendations": self._get_general_recommendations(),
                "detected_patterns": [],
                "evaluation_context": "All parameters within normal reference ranges" if evaluations else "No evaluation data",
                "disclaimer": self._get_disclaimer()
            }
        
        recommendations_list = []
        detected_conditions = []
        
        # PART 1: Process patterns (existing pattern-based logic preserved)
        for pattern in patterns:
            pattern_name = pattern.get("pattern")
            severity = pattern.get("severity", "Unknown")
            
            if pattern_name in self.medical_guidelines:
                guideline = self.medical_guidelines[pattern_name]
                recommendation = {
                    "condition": pattern_name,
                    "severity": severity,
                    "diet": guideline.get("diet", []),
                    "exercise": guideline.get("exercise", []),
                    "follow_up": guideline.get("follow_up", "Consult healthcare provider"),
                    "status": "✓ Guidelines available",
                    "evidence_source": "pattern-based"
                }
                
                # ENHANCEMENT: Add evaluation context if available
                if evaluations:
                    eval_context = self._get_evaluation_context(pattern_name, evaluations)
                    if eval_context:
                        recommendation["evaluation_context"] = eval_context
                        recommendation["evidence_source"] = "pattern + evaluation"
                
                recommendations_list.append(recommendation)
                detected_conditions.append(pattern_name)
            else:
                # Pattern detected but no specific guidelines available
                recommendation = {
                    "condition": pattern_name,
                    "severity": severity,
                    "diet": ["Maintain balanced, nutritious diet with whole foods"],
                    "exercise": ["Maintain regular moderate physical activity"],
                    "follow_up": "Consult healthcare provider for condition-specific guidance",
                    "status": "⚠ Generic recommendations provided",
                    "evidence_source": "pattern-based"
                }
                recommendations_list.append(recommendation)
                detected_conditions.append(pattern_name)
        
        # PART 2: Add evaluation-specific insights (new capability)
        if evaluations:
            eval_insights = self._generate_evaluation_insights(evaluations)
            if eval_insights:
                recommendations_list.extend(eval_insights)
        
        # Build comprehensive response
        response = {
            "status": "success",
            "detected_patterns_count": len(patterns),
            "detected_conditions": detected_conditions,
            "recommendations": recommendations_list,
            "general_lifestyle": self._get_general_lifestyle_tips(),
            "disclaimer": self._get_disclaimer()
        }
        
        # Add evaluation summary if available
        if evaluations:
            response["evaluation_summary"] = {
                "total_parameters": evaluations.get("total_parameters_evaluated", 0),
                "abnormal_count": len(evaluations.get("abnormal_findings", [])),
                "critical_count": len(evaluations.get("critical_findings", [])),
                "interpretation": evaluations.get("summary", {}).get("interpretation", "")
            }
        
        return response
    
    def _get_general_recommendations(self) -> List[Dict[str, Any]]:
        """Get general wellness recommendations for healthy individuals."""
        return [
            {
                "condition": "General Wellness",
                "diet": [
                    "Maintain a balanced diet with varied fruits, vegetables, whole grains, and lean proteins",
                    "Stay hydrated by drinking 8-10 glasses of water daily",
                    "Limit processed foods, added sugars, and excessive salt",
                    "Practice portion control and regular meal timing"
                ],
                "exercise": [
                    "Engage in at least 150 minutes of moderate-intensity aerobic activity weekly",
                    "Include resistance training 2-3 times per week",
                    "Maintain flexibility and balance through yoga or stretching",
                    "Avoid prolonged sedentary periods"
                ],
                "follow_up": "Regular annual health checkups and preventive screening recommended"
            }
        ]
    
    def _get_evaluation_context(
        self, 
        pattern_name: str, 
        evaluations: Dict[str, Any]
    ) -> str:
        """
        Get evaluation context for a detected pattern.
        
        Links pattern to specific parameter evaluations.
        
        Args:
            pattern_name: Name of detected pattern
            evaluations: Evaluation results from Phase 3A
        
        Returns:
            Context string describing reference-based evidence
        """
        abnormal_findings = evaluations.get('abnormal_findings', [])
        
        # Map patterns to relevant parameters
        pattern_parameter_map = {
            "Anemia Indicator": ["Hemoglobin", "RBC", "Hematocrit"],
            "Diabetes Risk": ["Glucose", "HbA1c"],
            "High Cholesterol": ["Cholesterol Total", "LDL", "HDL", "Triglycerides"],
            "Kidney Function Alert": ["Creatinine", "BUN"],
            "Liver Function Alert": ["ALT", "AST", "Bilirubin Total"]
        }
        
        relevant_params = pattern_parameter_map.get(pattern_name, [])
        
        # Find matching abnormal findings
        matching_findings = [
            f for f in abnormal_findings 
            if f['parameter'] in relevant_params
        ]
        
        if matching_findings:
            context_parts = []
            for finding in matching_findings:
                context_parts.append(
                    f"{finding['parameter']}: {finding['status']} ({finding['severity']})"
                )
            return "Reference-based evaluation: " + "; ".join(context_parts)
        
        return ""
    
    def _generate_evaluation_insights(
        self, 
        evaluations: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate additional recommendations from evaluation results.
        
        Captures abnormalities not covered by pattern recognition.
        
        Args:
            evaluations: Evaluation results from Phase 3A
        
        Returns:
            List of additional recommendations based on evaluation
        """
        insights = []
        abnormal_findings = evaluations.get('abnormal_findings', [])
        
        # Get parameters that aren't already covered by patterns
        pattern_flags = evaluations.get('flags_for_pattern_recognition', [])
        covered_params = set()
        for flag in pattern_flags:
            covered_params.update(flag.get('triggered_by', []))
        
        # Find uncovered abnormalities
        uncovered = [
            f for f in abnormal_findings 
            if f['parameter'] not in covered_params
        ]
        
        # Generate insights for uncovered abnormalities
        for finding in uncovered:
            param = finding['parameter']
            status = finding['status']
            severity = finding.get('severity', 'Unknown')
            
            # Generate targeted recommendations based on parameter
            insight = {
                "condition": f"{param} - {status}",
                "severity": severity,
                "diet": self._get_parameter_diet_advice(param, status),
                "exercise": self._get_parameter_exercise_advice(param, status),
                "follow_up": f"Discuss {param} levels with healthcare provider. Monitor and retest as recommended.",
                "status": "✓ Evidence-based (reference ranges)",
                "evidence_source": "evaluation-only"
            }
            insights.append(insight)
        
        return insights
    
    def _get_parameter_diet_advice(self, parameter: str, status: str) -> List[str]:
        """Get diet advice for specific parameter abnormality."""
        param_lower = parameter.lower()
        
        if 'wbc' in param_lower or 'white blood' in param_lower:
            if 'high' in status.lower():
                return [
                    "Focus on anti-inflammatory foods (berries, fatty fish, leafy greens)",
                    "Avoid processed foods and excessive sugar",
                    "Stay well-hydrated"
                ]
            else:
                return [
                    "Include immune-boosting foods (citrus fruits, yogurt, garlic)",
                    "Ensure adequate protein intake",
                    "Maintain balanced nutrition"
                ]
        
        elif 'platelet' in param_lower:
            if 'low' in status.lower():
                return [
                    "Include foods rich in vitamin K (leafy greens, broccoli)",
                    "Ensure adequate folate and vitamin B12 intake",
                    "Avoid alcohol"
                ]
        
        elif 'sodium' in param_lower or 'potassium' in param_lower:
            if 'high' in status.lower():
                return [
                    f"Reduce dietary {parameter.lower()} intake",
                    "Consult dietitian for specific guidance",
                    "Read food labels carefully"
                ]
        
        # Default advice
        return [
            "Maintain balanced, nutritious diet",
            "Consult healthcare provider for parameter-specific dietary guidance",
            "Consider referral to registered dietitian"
        ]
    
    def _get_parameter_exercise_advice(self, parameter: str, status: str) -> List[str]:
        """Get exercise advice for specific parameter abnormality."""
        # Conservative exercise recommendations for most abnormalities
        return [
            "Consult healthcare provider before starting new exercise program",
            "Start with light to moderate activity as tolerated",
            "Gradually increase intensity under medical supervision",
            "Monitor symptoms and adjust activity accordingly"
        ]
    
    def _get_general_lifestyle_tips(self) -> Dict[str, List[str]]:
        """Get general lifestyle tips applicable to all."""
        return {
            "sleep": [
                "Aim for 7-9 hours of quality sleep nightly",
                "Maintain consistent sleep schedule",
                "Create a cool, dark, quiet sleep environment",
                "Avoid screens 30 minutes before bedtime"
            ],
            "stress_management": [
                "Practice meditation or mindfulness (10-15 minutes daily)",
                "Engage in relaxation techniques (deep breathing, progressive muscle relaxation)",
                "Maintain social connections and support networks",
                "Seek professional help if experiencing chronic stress or anxiety"
            ],
            "preventive_care": [
                "Annual health checkups and screening tests based on age and risk factors",
                "Maintain vaccinations as recommended",
                "Avoid smoking and limit alcohol consumption",
                "Regular monitoring of vital signs (blood pressure, weight)"
            ]
        }
    
    def _get_disclaimer(self) -> str:
        """Get medical disclaimer for all recommendations."""
        return (
            "DISCLAIMER: This recommendation engine provides general lifestyle guidance based on "
            "clinical patterns and guidelines. It does NOT replace professional medical advice. "
            "Always consult with qualified healthcare providers for personalized medical recommendations, "
            "diagnosis, and treatment. The user assumes full responsibility for any decisions made "
            "based on this information."
        )
    
    def get_available_conditions(self) -> List[str]:
        """
        Get list of all conditions with available guidelines.
        
        Returns:
            List of condition names with available medical guidelines.
        """
        return sorted(list(self.medical_guidelines.keys()))
    
    def get_condition_details(self, condition_name: str) -> Dict[str, Any]:
        """
        Get detailed guidelines for a specific condition.
        
        Args:
            condition_name: Name of the condition
            
        Returns:
            Dictionary with condition guidelines, or None if not found.
        """
        return self.medical_guidelines.get(condition_name)


class SafetyValidator:
    """Validates recommendations for safety and clinical appropriateness."""
    
    @staticmethod
    def validate_recommendations(recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate generated recommendations for safety concerns.
        
        Args:
            recommendations: Output from RecommendationEngine
            
        Returns:
            Validation result with any warnings or issues.
        """
        validation_result = {
            "is_safe": True,
            "warnings": [],
            "info": []
        }
        
        # Check that disclaimer is present
        if "disclaimer" not in recommendations:
            validation_result["is_safe"] = False
            validation_result["warnings"].append("Missing medical disclaimer")
        
        # Check for multiple critical conditions that need urgent care
        critical_conditions = [
            "Elevated Kidney Parameters",
            "Elevated Liver Enzymes"
        ]
        
        detected = recommendations.get("detected_conditions", [])
        critical_detected = [c for c in detected if c in critical_conditions]
        
        if len(critical_detected) >= 2:
            validation_result["warnings"].append(
                f"Multiple serious conditions detected: {', '.join(critical_detected)}. "
                "Immediate medical consultation strongly recommended."
            )
        
        # Add info about limitations
        validation_result["info"].append(
            "These recommendations are based on detected patterns and general medical guidelines. "
            "Individual response may vary based on personal medical history, medications, and other factors."
        )
        
        return validation_result


def format_recommendations_for_display(recommendations: Dict[str, Any]) -> str:
    """
    Format recommendations for professional display/printing.
    
    Args:
        recommendations: Output from RecommendationEngine
        
    Returns:
        Formatted string suitable for display/printing.
    """
    output = []
    output.append("\n" + "="*70)
    output.append("MEDICAL RISK ANALYSIS & LIFESTYLE RECOMMENDATIONS")
    output.append("="*70)
    
    # Detected conditions section
    conditions = recommendations.get("detected_conditions", [])
    if conditions:
        output.append("\n📋 DETECTED CONDITIONS:")
        for i, condition in enumerate(conditions, 1):
            output.append(f"  {i}. {condition}")
    else:
        output.append("\n✓ NO ABNORMAL PATTERNS DETECTED")
        output.append("   General wellness recommendations apply.")
    
    # Recommendations section
    recs_list = recommendations.get("recommendations", [])
    if recs_list:
        output.append("\n" + "-"*70)
        output.append("PERSONALIZED LIFESTYLE RECOMMENDATIONS:")
        output.append("-"*70)
        
        for i, rec in enumerate(recs_list, 1):
            output.append(f"\n{i}. {rec.get('condition', 'Recommendation')}")
            if rec.get('severity'):
                output.append(f"   Severity: {rec['severity']}")
            
            # Diet recommendations
            diet_items = rec.get('diet', [])
            if diet_items:
                output.append("\n   🥗 DIET:")
                for item in diet_items:
                    output.append(f"      • {item}")
            
            # Exercise recommendations
            exercise_items = rec.get('exercise', [])
            if exercise_items:
                output.append("\n   💪 EXERCISE:")
                for item in exercise_items:
                    output.append(f"      • {item}")
            
            # Follow-up recommendations
            follow_up = rec.get('follow_up')
            if follow_up:
                output.append(f"\n   📅 FOLLOW-UP: {follow_up}")
    
    # General lifestyle tips
    lifestyle = recommendations.get('general_lifestyle', {})
    if lifestyle:
        output.append("\n" + "-"*70)
        output.append("GENERAL LIFESTYLE RECOMMENDATIONS:")
        output.append("-"*70)
        
        for category, tips in lifestyle.items():
            category_name = category.replace('_', ' ').title()
            output.append(f"\n{category_name}:")
            for tip in tips:
                output.append(f"   • {tip}")
    
    # Disclaimer
    output.append("\n" + "="*70)
    output.append("⚠️  MEDICAL DISCLAIMER:")
    output.append("="*70)
    output.append(recommendations.get('disclaimer', ''))
    output.append("="*70 + "\n")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    engine = RecommendationEngine()
    
    # Example patterns from Phase 2 Model (Pattern Recognition)
    example_patterns = [
        {"pattern": "Anemia Indicator", "severity": "Mild"},
        {"pattern": "High Cholesterol", "severity": "Moderate"}
    ]
    
    # Generate recommendations
    recommendations = engine.generate_recommendations(example_patterns)
    
    # Validate recommendations
    validation = SafetyValidator.validate_recommendations(recommendations)
    
    # Display formatted output
    print(format_recommendations_for_display(recommendations))
    
    # Print validation results
    if validation["warnings"]:
        print("\n⚠️  VALIDATION WARNINGS:")
        for warning in validation["warnings"]:
            print(f"   • {warning}")
    
    print("\n📌 AVAILABLE CONDITIONS IN KNOWLEDGE BASE:")
    conditions = engine.get_available_conditions()
    for condition in conditions:
        print(f"   • {condition}")
