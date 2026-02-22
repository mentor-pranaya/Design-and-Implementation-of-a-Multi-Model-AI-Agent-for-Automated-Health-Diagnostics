"""
Contextual Model - Phase 3D (Model 3)
True personalized clinical reasoning through contextual refinement.

This module represents the final layer of the multi-model AI agent that:
1. Takes evaluated parameters (Model 1: Reference-based evaluation)
2. Takes detected patterns (Model 2: Pattern recognition)
3. Refines risk scores and interpretations based on patient context
4. Adds personalized risk modifiers and explanations

Architecture Position:
Phase 2 (Extraction) → 
Phase 3A (Evaluation - Model 1) → 
Phase 3B (Pattern Detection - Model 2) → 
Phase 3D (Contextual Refinement - Model 3) → 
Phase 3C (Recommendations)

Design Philosophy:
- Personalized: Every patient is unique, context matters
- Clinically sound: Age, gender, history, lifestyle influence interpretation
- Explainable: Every adjustment has a clear rationale
- Evidence-based: Contextual factors are medically recognized risk modifiers

CONTEXT-AWARE RISK FACTORS:
1. Age: Thresholds and severity vary by age (pediatric, adult, geriatric)
2. Gender: Different normal ranges and risk profiles
3. Medical History: Known conditions amplify related parameter risks
4. Lifestyle: Smoking, exercise, diet, alcohol affect interpretation
"""

from typing import Dict, Any, List, Optional


class ContextualRefiner:
    """
    Contextual refinement engine that personalizes clinical interpretation.
    
    This is Model 3 in the multi-model architecture, providing the critical
    layer of personalization that transforms generic evaluations into
    patient-specific clinical insights.
    
    Key Responsibilities:
    - Apply age-based risk adjustments
    - Apply gender-based interpretations
    - Amplify risks based on medical history
    - Integrate lifestyle factors into risk assessment
    - Generate explainable contextual modifiers
    """
    
    def __init__(self, patient_info: Dict[str, Any]):
        """
        Initialize the contextual refiner with patient information.
        
        Args:
            patient_info: Comprehensive patient context including:
                - age: Patient age in years
                - sex: "male" or "female"
                - known_conditions: List of diagnosed conditions
                  e.g., ["diabetes", "hypertension", "ckd"]
                - lifestyle: Dictionary with lifestyle factors
                  {
                    "smoker": bool,
                    "exercise_level": "low" | "moderate" | "high",
                    "diet_type": "vegetarian" | "mixed" | "high_protein",
                    "alcohol_use": "none" | "moderate" | "heavy"
                  }
        """
        self.patient_info = patient_info or {}
        self.age = self.patient_info.get("age")
        self.sex = self.patient_info.get("sex")
        self.known_conditions = self.patient_info.get("known_conditions", [])
        self.lifestyle = self.patient_info.get("lifestyle", {})
        
        # Normalize known conditions to lowercase for case-insensitive matching
        self.known_conditions = [cond.lower() for cond in self.known_conditions]
        
        print(f"✓ Contextual Refiner initialized for {self.sex or 'unknown'} patient, age {self.age or 'unknown'}")
        if self.known_conditions:
            print(f"  - Known conditions: {', '.join(self.known_conditions)}")
        if self.lifestyle:
            print(f"  - Lifestyle factors: {self._format_lifestyle()}")
    
    def _format_lifestyle(self) -> str:
        """Format lifestyle factors for display."""
        factors = []
        if self.lifestyle.get("smoker"):
            factors.append("smoker")
        if self.lifestyle.get("exercise_level"):
            factors.append(f"exercise: {self.lifestyle['exercise_level']}")
        if self.lifestyle.get("diet_type"):
            factors.append(f"diet: {self.lifestyle['diet_type']}")
        if self.lifestyle.get("alcohol_use"):
            factors.append(f"alcohol: {self.lifestyle['alcohol_use']}")
        return ", ".join(factors) if factors else "none specified"
    
    def refine(
        self,
        evaluated_parameters: Dict[str, Any],
        detected_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Refine evaluation and pattern results with patient context.
        
        This is the main entry point for contextual refinement.
        
        Args:
            evaluated_parameters: Results from Phase 3A (reference-based evaluation)
            detected_patterns: Results from Phase 3B (pattern recognition)
        
        Returns:
            Refined output with contextual adjustments:
            {
                "evaluated_parameters": {...},  # Original evaluations
                "detected_patterns": {...},     # Patterns with contextual refinements
                "contextual_modifiers": [...],  # Global contextual insights
                "personalization_summary": {...} # Summary of adjustments made
            }
        """
        print("\n" + "="*70)
        print("Phase 3D: Applying Contextual Refinements (Model 3)")
        print("="*70)
        
        # Deep copy to avoid modifying originals
        import copy
        refined_output = {
            "evaluated_parameters": copy.deepcopy(evaluated_parameters),
            "detected_patterns": copy.deepcopy(detected_patterns),
            "contextual_modifiers": [],
            "personalization_summary": {
                "age_based_adjustments": 0,
                "gender_based_adjustments": 0,
                "history_based_adjustments": 0,
                "lifestyle_based_adjustments": 0
            }
        }
        
        # Apply domain-specific refinements
        self._refine_cardiovascular_risk(refined_output)
        self._refine_diabetes_risk(refined_output)
        self._refine_kidney_risk(refined_output)
        self._refine_anemia_risk(refined_output)
        self._refine_liver_risk(refined_output)
        
        # Add global contextual insights
        self._add_global_modifiers(refined_output)
        
        # Generate summary
        self._generate_summary(refined_output)
        
        return refined_output
    
    # =========================================================================
    # DOMAIN-SPECIFIC REFINEMENT METHODS
    # =========================================================================
    
    def _refine_cardiovascular_risk(self, output: Dict[str, Any]) -> None:
        """
        Refine cardiovascular risk interpretation based on context.
        
        Risk Amplifiers:
        - Age > 50: 1.1x multiplier
        - Smoking: 1.15x multiplier (major CV risk factor)
        - Known hypertension: 1.1x multiplier
        - Known diabetes: 1.1x multiplier (CV disease risk)
        - Sedentary lifestyle: 1.05x multiplier
        - Heavy alcohol use: 1.05x multiplier
        """
        patterns = output.get("detected_patterns", {})
        
        # Check for cardiovascular-related patterns
        cv_patterns = [k for k in patterns.keys() if "cardiovascular" in k.lower() or "cholesterol" in k.lower()]
        
        if not cv_patterns:
            return
        
        for pattern_key in cv_patterns:
            risk_data = patterns[pattern_key]
            modifiers = []
            original_risk = risk_data.get("risk_score", 0)
            adjusted_risk = original_risk
            
            # Age-based amplification
            if self.age and self.age > 50:
                adjusted_risk *= 1.1
                modifiers.append(f"Risk amplified due to age {self.age} (>50 years)")
                output["personalization_summary"]["age_based_adjustments"] += 1
            
            # Smoking increases CV risk significantly
            if self.lifestyle.get("smoker"):
                adjusted_risk *= 1.15
                modifiers.append("Risk significantly elevated due to smoking (major CV risk factor)")
                output["personalization_summary"]["lifestyle_based_adjustments"] += 1
            
            # Hypertension history
            if "hypertension" in self.known_conditions or "htn" in self.known_conditions:
                adjusted_risk *= 1.1
                modifiers.append("Risk elevated due to known hypertension")
                output["personalization_summary"]["history_based_adjustments"] += 1
            
            # Diabetes amplifies CV risk
            if "diabetes" in self.known_conditions or "dm" in self.known_conditions:
                adjusted_risk *= 1.1
                modifiers.append("Risk elevated due to diabetes (cardiovascular disease risk)")
                output["personalization_summary"]["history_based_adjustments"] += 1
            
            # Sedentary lifestyle
            if self.lifestyle.get("exercise_level") == "low":
                adjusted_risk *= 1.05
                modifiers.append("Risk increased due to sedentary lifestyle")
                output["personalization_summary"]["lifestyle_based_adjustments"] += 1
            
            # Heavy alcohol use
            if self.lifestyle.get("alcohol_use") == "heavy":
                adjusted_risk *= 1.05
                modifiers.append("Risk increased due to heavy alcohol consumption")
                output["personalization_summary"]["lifestyle_based_adjustments"] += 1
            
            # Apply adjustments
            if modifiers:
                risk_data["risk_score"] = min(adjusted_risk, 1.0)  # Cap at 1.0
                risk_data["contextual_adjustments"] = modifiers
                risk_data["original_risk_score"] = original_risk
                print(f"  ✓ Cardiovascular risk adjusted: {original_risk:.2f} → {risk_data['risk_score']:.2f}")
    
    def _refine_diabetes_risk(self, output: Dict[str, Any]) -> None:
        """
        Refine diabetes/metabolic risk interpretation based on context.
        
        Risk Modifiers:
        - Known diabetes: Context flag (disease management interpretation)
        - Age > 45: 1.05x multiplier (increased diabetes risk)
        - Sedentary lifestyle: 1.08x multiplier (major metabolic risk)
        - Family history: 1.1x multiplier (if we add this data later)
        """
        patterns = output.get("detected_patterns", {})
        
        diabetes_patterns = [k for k in patterns.keys() if "diabetes" in k.lower() or "glucose" in k.lower() or "metabolic" in k.lower()]
        
        if not diabetes_patterns:
            return
        
        for pattern_key in diabetes_patterns:
            risk_data = patterns[pattern_key]
            modifiers = []
            original_risk = risk_data.get("risk_score", 0)
            adjusted_risk = original_risk
            
            # Known diabetes - interpretive context
            if "diabetes" in self.known_conditions or "dm" in self.known_conditions:
                modifiers.append("Known diabetic – interpretation reflects disease management status")
                output["personalization_summary"]["history_based_adjustments"] += 1
            
            # Age-based risk (diabetes increases with age)
            if self.age and self.age > 45:
                adjusted_risk *= 1.05
                modifiers.append(f"Age {self.age} increases metabolic risk (>45 years)")
                output["personalization_summary"]["age_based_adjustments"] += 1
            
            # Sedentary lifestyle - major metabolic risk factor
            if self.lifestyle.get("exercise_level") == "low":
                adjusted_risk *= 1.08
                modifiers.append("Sedentary lifestyle significantly increases metabolic risk")
                output["personalization_summary"]["lifestyle_based_adjustments"] += 1
            
            # Apply adjustments
            if modifiers:
                risk_data["risk_score"] = min(adjusted_risk, 1.0)
                risk_data["contextual_adjustments"] = modifiers
                risk_data["original_risk_score"] = original_risk
                print(f"  ✓ Diabetes risk adjusted: {original_risk:.2f} → {risk_data['risk_score']:.2f}")
    
    def _refine_kidney_risk(self, output: Dict[str, Any]) -> None:
        """
        Refine kidney function interpretation based on context.
        
        Risk Modifiers:
        - Known CKD: Stricter interpretation flag
        - Age > 60: Age-related decline context
        - Known diabetes: 1.1x (diabetic nephropathy risk)
        - Known hypertension: 1.05x (hypertensive nephropathy)
        """
        patterns = output.get("detected_patterns", {})
        
        kidney_patterns = [k for k in patterns.keys() if "kidney" in k.lower() or "renal" in k.lower() or "creatinine" in k.lower()]
        
        if not kidney_patterns:
            return
        
        for pattern_key in kidney_patterns:
            risk_data = patterns[pattern_key]
            modifiers = []
            original_risk = risk_data.get("risk_score", 0)
            adjusted_risk = original_risk
            
            # Pre-existing CKD
            if "ckd" in self.known_conditions or "chronic kidney disease" in self.known_conditions:
                modifiers.append("Pre-existing CKD – stricter interpretation applied")
                adjusted_risk *= 1.15
                output["personalization_summary"]["history_based_adjustments"] += 1
            
            # Age-related decline
            if self.age and self.age > 60:
                modifiers.append(f"Age-related renal decline considered (age {self.age})")
                output["personalization_summary"]["age_based_adjustments"] += 1
            
            # Diabetes increases kidney risk
            if "diabetes" in self.known_conditions or "dm" in self.known_conditions:
                adjusted_risk *= 1.1
                modifiers.append("Diabetic nephropathy risk considered")
                output["personalization_summary"]["history_based_adjustments"] += 1
            
            # Hypertension affects kidneys
            if "hypertension" in self.known_conditions or "htn" in self.known_conditions:
                adjusted_risk *= 1.05
                modifiers.append("Hypertensive nephropathy risk considered")
                output["personalization_summary"]["history_based_adjustments"] += 1
            
            # Apply adjustments
            if modifiers:
                risk_data["risk_score"] = min(adjusted_risk, 1.0)
                risk_data["contextual_adjustments"] = modifiers
                risk_data["original_risk_score"] = original_risk
                print(f"  ✓ Kidney function risk adjusted: {original_risk:.2f} → {risk_data['risk_score']:.2f}")
    
    def _refine_anemia_risk(self, output: Dict[str, Any]) -> None:
        """
        Refine anemia interpretation based on context.
        
        Risk Modifiers:
        - Gender-specific: Females have different hemoglobin ranges
        - Vegetarian diet: Iron deficiency risk (1.1x)
        - Known anemia: Disease management context
        - Age-specific adjustments
        """
        patterns = output.get("detected_patterns", {})
        
        anemia_patterns = [k for k in patterns.keys() if "anemia" in k.lower() or "iron" in k.lower()]
        
        if not anemia_patterns:
            return
        
        for pattern_key in anemia_patterns:
            risk_data = patterns[pattern_key]
            modifiers = []
            original_risk = risk_data.get("risk_score", 0)
            adjusted_risk = original_risk
            
            # Gender-based interpretation
            if self.sex == "female":
                modifiers.append("Female-specific hemoglobin ranges applied")
                output["personalization_summary"]["gender_based_adjustments"] += 1
            
            # Vegetarian diet - iron deficiency risk
            if self.lifestyle.get("diet_type") == "vegetarian":
                adjusted_risk *= 1.1
                modifiers.append("Vegetarian diet increases iron deficiency risk")
                output["personalization_summary"]["lifestyle_based_adjustments"] += 1
            
            # Known anemia
            if "anemia" in self.known_conditions:
                modifiers.append("Known anemia – monitoring disease management")
                output["personalization_summary"]["history_based_adjustments"] += 1
            
            # Apply adjustments
            if modifiers:
                risk_data["risk_score"] = min(adjusted_risk, 1.0)
                risk_data["contextual_adjustments"] = modifiers
                risk_data["original_risk_score"] = original_risk
                print(f"  ✓ Anemia risk adjusted: {original_risk:.2f} → {risk_data['risk_score']:.2f}")
    
    def _refine_liver_risk(self, output: Dict[str, Any]) -> None:
        """
        Refine liver function interpretation based on context.
        
        Risk Modifiers:
        - Heavy alcohol use: 1.2x multiplier (major liver risk)
        - Moderate alcohol: 1.1x multiplier
        - Known liver disease: Stricter interpretation
        """
        patterns = output.get("detected_patterns", {})
        
        liver_patterns = [k for k in patterns.keys() if "liver" in k.lower() or "hepatic" in k.lower()]
        
        if not liver_patterns:
            return
        
        for pattern_key in liver_patterns:
            risk_data = patterns[pattern_key]
            modifiers = []
            original_risk = risk_data.get("risk_score", 0)
            adjusted_risk = original_risk
            
            # Alcohol use significantly affects liver
            if self.lifestyle.get("alcohol_use") == "heavy":
                adjusted_risk *= 1.2
                modifiers.append("Heavy alcohol use significantly increases liver risk")
                output["personalization_summary"]["lifestyle_based_adjustments"] += 1
            elif self.lifestyle.get("alcohol_use") == "moderate":
                adjusted_risk *= 1.1
                modifiers.append("Moderate alcohol use increases liver risk")
                output["personalization_summary"]["lifestyle_based_adjustments"] += 1
            
            # Known liver disease
            if any(cond in self.known_conditions for cond in ["liver disease", "cirrhosis", "hepatitis"]):
                modifiers.append("Known liver disease – stricter monitoring required")
                adjusted_risk *= 1.15
                output["personalization_summary"]["history_based_adjustments"] += 1
            
            # Apply adjustments
            if modifiers:
                risk_data["risk_score"] = min(adjusted_risk, 1.0)
                risk_data["contextual_adjustments"] = modifiers
                risk_data["original_risk_score"] = original_risk
                print(f"  ✓ Liver function risk adjusted: {original_risk:.2f} → {risk_data['risk_score']:.2f}")
    
    def _add_global_modifiers(self, output: Dict[str, Any]) -> None:
        """
        Add global contextual insights that apply across all evaluations.
        """
        global_modifiers = []
        
        # Age-related global context
        if self.age:
            if self.age < 18:
                global_modifiers.append("Pediatric ranges and interpretations applied")
            elif self.age > 65:
                global_modifiers.append("Geriatric considerations: age-related physiological changes considered")
        
        # High-risk lifestyle combination
        if self.lifestyle.get("smoker") and self.lifestyle.get("exercise_level") == "low":
            global_modifiers.append("High-risk lifestyle combination: smoking + sedentary behavior significantly increases multiple health risks")
        
        # Multiple chronic conditions
        if len(self.known_conditions) >= 2:
            global_modifiers.append(f"Multiple chronic conditions ({len(self.known_conditions)}) increase overall health complexity")
        
        output["contextual_modifiers"] = global_modifiers
    
    def _generate_summary(self, output: Dict[str, Any]) -> None:
        """Generate a human-readable summary of personalization."""
        summary = output["personalization_summary"]
        total_adjustments = sum(summary.values())
        
        if total_adjustments > 0:
            print(f"\n✓ Applied {total_adjustments} contextual adjustments:")
            if summary["age_based_adjustments"] > 0:
                print(f"  - {summary['age_based_adjustments']} age-based adjustments")
            if summary["gender_based_adjustments"] > 0:
                print(f"  - {summary['gender_based_adjustments']} gender-based adjustments")
            if summary["history_based_adjustments"] > 0:
                print(f"  - {summary['history_based_adjustments']} medical history adjustments")
            if summary["lifestyle_based_adjustments"] > 0:
                print(f"  - {summary['lifestyle_based_adjustments']} lifestyle-based adjustments")
        else:
            print("\n✓ No contextual adjustments needed (insufficient context or no risk patterns)")
        
        print("="*70)


# =========================================================================
# UTILITY FUNCTIONS
# =========================================================================

def apply_contextual_refinement(
    evaluated_parameters: Dict[str, Any],
    detected_patterns: Dict[str, Any],
    patient_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to apply contextual refinement.
    
    Args:
        evaluated_parameters: Results from Phase 3A
        detected_patterns: Results from Phase 3B
        patient_info: Patient context
    
    Returns:
        Refined results with contextual adjustments
    """
    refiner = ContextualRefiner(patient_info)
    return refiner.refine(evaluated_parameters, detected_patterns)
