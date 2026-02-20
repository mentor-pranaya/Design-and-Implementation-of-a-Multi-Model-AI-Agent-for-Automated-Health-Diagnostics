"""
Enhanced Recommendation Engine: Context-aware clinical recommendations.

Generates targeted, parameter-specific, urgency-aware recommendations
with dynamic tone and escalation based on clinical severity.

Production-grade intelligent recommendation synthesis.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from risk_aggregator import UrgencyLevel

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """Single recommendation with context and urgency."""
    text: str
    category: str  # "lifestyle", "medical", "testing", "monitoring", "urgent"
    urgency: UrgencyLevel
    priority: int  # 1 (highest) to 5 (lowest)
    parameter_related: Optional[str] = None
    evidence_level: str = "clinical"  # "clinical", "preventive", "lifestyle"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "category": self.category,
            "urgency": self.urgency.value,
            "priority": self.priority,
            "parameter_related": self.parameter_related,
            "evidence_level": self.evidence_level
        }


class RecommendationEngine:
    """
    Generates context-aware clinical recommendations.
    
    Produces recommendations based on:
    - Severity level and urgency
    - Specific parameter abnormalities
    - Patient demographics
    - Medical history
    - Parameter interactions
    """
    
    # Parameter-specific recommendations
    PARAMETER_RECOMMENDATIONS = {
        "glucose": {
            "critical": [
                "Seek immediate medical attention for blood glucose crisis",
                "Monitor blood glucose immediately with portable glucose meter",
                "Avoid physical exertion until evaluated by physician"
            ],
            "high": [
                "Consult endocrinologist or diabetes specialist within 1-2 days",
                "Begin glucose monitoring 2-3 times daily",
                "Reduce refined carbohydrates and sugar intake",
                "Increase physical activity to 30 minutes daily"
            ],
            "moderate": [
                "Schedule appointment with primary care physician",
                "Start daily glucose monitoring",
                "Implement dietary changes (reduce processed foods)",
                "Increase water intake"
            ]
        },
        "hemoglobin": {
            "critical": [
                "Seek urgent medical evaluation for severe anemia",
                "May require immediate blood transfusion",
                "Avoid strenuous activity"
            ],
            "high": [
                "Urgent hematology consultation recommended",
                "Increase iron-rich foods (red meat, spinach, legumes)",
                "Take iron supplements as directed by physician",
                "Retest hemoglobin in 2-4 weeks"
            ],
            "moderate": [
                "Discuss iron supplementation with healthcare provider",
                "Increase dietary iron intake",
                "Retest in 4-6 weeks"
            ]
        },
        "total_cholesterol": {
            "critical": [
                "Immediate cardiology evaluation recommended",
                "Consider statin therapy after physician evaluation",
                "Strict dietary modification required"
            ],
            "high": [
                "Consult cardiologist or primary care physician",
                "Reduce saturated fat intake significantly",
                "Increase soluble fiber (oats, beans, fruits)",
                "Regular aerobic exercise 5 days/week",
                "Consider pharmaceutical intervention"
            ],
            "moderate": [
                "Schedule appointment with healthcare provider",
                "Implement Mediterranean or DASH diet",
                "Increase physical activity",
                "Recheck cholesterol in 3 months"
            ]
        },
        "hdl": {
            "high": [
                "Excellent cardiovascular risk profile",
                "Maintain current exercise and diet routine"
            ],
            "low": [
                "Increase aerobic exercise to 30 minutes daily, 5 days/week",
                "Increase fish intake (omega-3 fatty acids)",
                "Reduce alcohol if intake is excessive",
                "Avoid smoking and secondhand smoke"
            ]
        },
        "ldl": {
            "critical": [
                "Immediate cardiology evaluation required",
                "Strong consideration for statin therapy",
                "Aggressive dietary modification"
            ],
            "high": [
                "Cardiology consultation recommended",
                "Reduce LDL through diet (eliminate trans fats, limit saturated fat)",
                "Consider statins if lifestyle changes insufficient",
                "Regular cardiovascular monitoring"
            ],
            "moderate": [
                "Discuss treatment options with healthcare provider",
                "Implement heart-healthy diet",
                "Increase exercise"
            ]
        },
        "triglycerides": {
            "critical": [
                "Urgent medical evaluation for hypertriglyceridemia",
                "Risk of acute pancreatitis — seek immediate care if abdominal pain",
                "Strict dietary modification required"
            ],
            "high": [
                "Consult cardiologist or endocrinologist",
                "Dramatically reduce refined carbohydrates and sugar",
                "Eliminate alcohol consumption",
                "Increase omega-3 fatty acids (fish oil supplements may be recommended)",
                "Consider fibrate or statin therapy"
            ],
            "moderate": [
                "Schedule appointment with healthcare provider",
                "Reduce simple carbohydrates and alcohol",
                "Increase physical activity",
                "Recheck in 3 months"
            ]
        },
        "creatinine": {
            "critical": [
                "Urgent nephrology evaluation for severe renal dysfunction",
                "May require dialysis referral",
                "Strict fluid and electrolyte management"
            ],
            "high": [
                "Immediate nephrology or primary care evaluation",
                "Check kidney function (GFR) regularly",
                "Reduce protein intake (consult nutritionist)",
                "Monitor blood pressure closely"
            ],
            "moderate": [
                "Schedule appointment to discuss kidney function",
                "Monitor fluid intake",
                "Reduce salt consumption"
            ]
        },
        "blood_pressure_systolic": {
            "critical": [
                "SEEK IMMEDIATE MEDICAL ATTENTION — hypertensive crisis risk",
                "Go to ER if experiencing chest pain, shortness of breath, or severe headache",
                "Do not exert yourself"
            ],
            "high": [
                "Urgent antihypertensive therapy consideration",
                "Strict salt reduction (target <2g/day)",
                "Daily exercise 30 minutes",
                "Stress reduction techniques",
                "Consider medications if lifestyle changes insufficient"
            ],
            "moderate": [
                "Healthcare provider appointment recommended",
                "Reduce sodium intake",
                "Increase potassium-rich foods",
                "Regular exercise"
            ]
        },
        "wbc": {
            "critical": [
                "Urgent evaluation for severe leukosis or infection",
                "May require specialist consultation (hematology/oncology)",
                "Avoid crowds to prevent infection"
            ],
            "high": [
                "Evaluate for infection or inflammatory condition",
                "Physician consultation recommended within 1-2 days",
                "Rest and increase fluid intake",
                "Monitor for fever or infection signs"
            ],
            "low": [
                "Evaluation for immunosuppression recommended",
                "Avoid crowds and sick individuals",
                "Additional testing may be needed"
            ]
        },
        "platelets": {
            "critical": [
                "URGENT hematology evaluation — severe bleeding risk",
                "Avoid trauma and anticoagulant medications",
                "Seek immediate care if unusual bleeding occurs"
            ],
            "high": [
                "Avoid NSAIDs and aspirin",
                "Be cautious to prevent injury",
                "Return for retest in 1 week"
            ],
            "low": [
                "Evaluation for thrombocytopenia recommended",
                "Avoid medications unless essential",
                "Report any unusual bleeding immediately"
            ]
        }
    }
    
    # Lifestyle recommendations by urgency
    LIFESTYLE_RECOMMENDATIONS = {
        UrgencyLevel.CRITICAL: [
            "Seek immediate professional medical evaluation",
            "Do not delay — your situation requires urgent care",
            "Avoid strenuous physical activity",
            "Monitor symptoms closely"
        ],
        UrgencyLevel.HIGH: [
            "Schedule medical appointment within 1-3 days",
            "Reduce physical activity to light exercise until cleared by physician",
            "Begin stress management techniques",
            "Improve sleep quality (7-9 hours nightly)"
        ],
        UrgencyLevel.MODERATE: [
            "Schedule routine medical appointment within 1-2 weeks",
            "Implement balanced diet (Mediterranean or DASH)",
            "Increase moderate physical activity to 30 minutes daily",
            "Practice stress reduction (yoga, meditation, deep breathing)",
            "Maintain healthy weight"
        ],
        UrgencyLevel.LOW: [
            "Continue regular health maintenance",
            "Maintain current healthy habits",
            "Annual health check-ups recommended",
            "Stay active with regular exercise"
        ]
    }
    
    def __init__(self):
        """Initialize recommendation engine."""
        logger.info("Recommendation engine initialized")
    
    def generate_recommendations(
        self,
        urgency_level: UrgencyLevel,
        abnormal_parameters: Dict[str, dict],
        age: Optional[int] = None,
        gender: Optional[str] = None,
        medical_history: Optional[List[str]] = None,
        max_recommendations: int = 10
    ) -> List[Recommendation]:
        """
        Generate context-aware recommendations.
        
        Args:
            urgency_level: Global urgency level
            abnormal_parameters: Dict of {param_name: {value, severity, ...}}
            age: Optional age
            gender: Optional gender
            medical_history: Optional list of conditions
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            List: Ranked recommendations
            
        Example:
            >>> engine = RecommendationEngine()
            >>> abnormal_params = {
            ...     "glucose": {"value": 250, "severity": "High"},
            ...     "cholesterol": {"value": 220, "severity": "High"}
            ... }
            >>> recs = engine.generate_recommendations(
            ...     urgency_level=UrgencyLevel.HIGH,
            ...     abnormal_parameters=abnormal_params,
            ...     age=55
            ... )
        """
        
        recommendations = []
        
        # Add urgency-level specific recommendations
        urgency_recs = self._get_urgency_recommendations(urgency_level)
        for rec_text in urgency_recs:
            recommendations.append(Recommendation(
                text=rec_text,
                category="urgent" if urgency_level in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH] else "medical",
                urgency=urgency_level,
                priority=1,
                evidence_level="clinical"
            ))
        
        # Add parameter-specific recommendations
        param_recs = self._get_parameter_recommendations(
            abnormal_parameters,
            urgency_level
        )
        recommendations.extend(param_recs)
        
        # Add demographic-specific recommendations
        demo_recs = self._get_demographic_recommendations(
            age=age,
            gender=gender,
            medical_history=medical_history
        )
        recommendations.extend(demo_recs)
        
        # Add preventive recommendations if not critical
        if urgency_level not in [UrgencyLevel.CRITICAL]:
            preventive_recs = self._get_preventive_recommendations(medical_history)
            recommendations.extend(preventive_recs)
        
        # Remove duplicates (keep highest priority version)
        recommendations = self._deduplicate_recommendations(recommendations)
        
        # Sort by priority (1 = highest)
        recommendations.sort(key=lambda r: (r.priority, r.urgency.value))
        
        # Return top N
        result = recommendations[:max_recommendations]
        
        logger.info(
            f"Generated {len(result)} recommendations for urgency={urgency_level.value}"
        )
        
        return result
    
    def _get_urgency_recommendations(self, urgency: UrgencyLevel) -> List[str]:
        """Get main recommendations based on urgency level."""
        return self.LIFESTYLE_RECOMMENDATIONS.get(urgency, [])
    
    def _get_parameter_recommendations(
        self,
        abnormal_parameters: Dict[str, dict],
        urgency: UrgencyLevel
    ) -> List[Recommendation]:
        """
        Generate parameter-specific recommendations.
        
        Args:
            abnormal_parameters: Dict of abnormal params with severity info
            urgency: Global urgency level
            
        Returns:
            List of Recommendation objects
        """
        
        recommendations = []
        
        for param_name, param_info in abnormal_parameters.items():
            severity = param_info.get("severity", "moderate").lower()
            
            # Get parameter-specific recommendations
            if param_name in self.PARAMETER_RECOMMENDATIONS:
                param_recs = self.PARAMETER_RECOMMENDATIONS[param_name]
                
                # Get recs for matching severity
                if severity == "critical" and "critical" in param_recs:
                    recs_list = param_recs["critical"]
                    priority = 1
                elif severity == "high" and "high" in param_recs:
                    recs_list = param_recs["high"]
                    priority = 2
                else:
                    recs_list = param_recs.get("moderate", [])
                    priority = 3
                
                for rec_text in recs_list:
                    recommendations.append(Recommendation(
                        text=rec_text,
                        category=self._categorize_recommendation(rec_text),
                        urgency=urgency,
                        priority=priority,
                        parameter_related=param_name,
                        evidence_level="clinical"
                    ))
        
        return recommendations
    
    def _get_demographic_recommendations(
        self,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        medical_history: Optional[List[str]] = None
    ) -> List[Recommendation]:
        """
        Generate demographic-specific recommendations.
        
        Args:
            age: Age in years
            gender: Gender
            medical_history: List of conditions
            
        Returns:
            List of Recommendation objects
        """
        
        recommendations = []
        
        # Age-specific recommendations
        if age:
            if age > 50:
                recommendations.append(Recommendation(
                    text="Cardiovascular risk assessment recommended (age-appropriate screening)",
                    category="medical",
                    urgency=UrgencyLevel.MODERATE,
                    priority=3,
                    evidence_level="preventive"
                ))
            
            if age > 60:
                recommendations.append(Recommendation(
                    text="Bone density screening recommended for age",
                    category="testing",
                    urgency=UrgencyLevel.MODERATE,
                    priority=4,
                    evidence_level="preventive"
                ))
        
        # Medical history-specific
        if medical_history:
            conditions = " ".join(medical_history).lower()
            
            if "diabetes" in conditions:
                recommendations.append(Recommendation(
                    text="Regular HbA1c testing (every 3 months) recommended for diabetes monitoring",
                    category="testing",
                    urgency=UrgencyLevel.MODERATE,
                    priority=2,
                    evidence_level="clinical"
                ))
            
            if "hypertension" in conditions:
                recommendations.append(Recommendation(
                    text="Daily blood pressure monitoring with home BP monitor recommended",
                    category="monitoring",
                    urgency=UrgencyLevel.MODERATE,
                    priority=2,
                    evidence_level="clinical"
                ))
            
            if "cardiovascular" in conditions or "heart" in conditions:
                recommendations.append(Recommendation(
                    text="Cardiology follow-up within 1 month",
                    category="medical",
                    urgency=UrgencyLevel.HIGH,
                    priority=1,
                    evidence_level="clinical"
                ))
        
        return recommendations
    
    def _get_preventive_recommendations(
        self,
        medical_history: Optional[List[str]] = None
    ) -> List[Recommendation]:
        """Get preventive health recommendations."""
        
        recommendations = []
        
        # Universal preventive recommendations
        recommendations.extend([
            Recommendation(
                text="Increase fruit and vegetable intake to 5+ servings daily",
                category="lifestyle",
                urgency=UrgencyLevel.MODERATE,
                priority=4,
                evidence_level="preventive"
            ),
            Recommendation(
                text="Regular exercise: 150 minutes moderate activity per week",
                category="lifestyle",
                urgency=UrgencyLevel.MODERATE,
                priority=4,
                evidence_level="preventive"
            ),
            Recommendation(
                text="Maintain healthy weight (BMI 18.5-24.9)",
                category="lifestyle",
                urgency=UrgencyLevel.MODERATE,
                priority=4,
                evidence_level="preventive"
            ),
            Recommendation(
                text="Avoid tobacco and limit alcohol consumption",
                category="lifestyle",
                urgency=UrgencyLevel.MODERATE,
                priority=4,
                evidence_level="preventive"
            )
        ])
        
        return recommendations
    
    def _categorize_recommendation(self, text: str) -> str:
        """Categorize recommendation by type."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["urgent", "immediate", "seek", "emergency"]):
            return "urgent"
        elif any(word in text_lower for word in ["diet", "exercise", "lifestyle", "activity"]):
            return "lifestyle"
        elif any(word in text_lower for word in ["test", "retest", "screening", "monitor"]):
            return "monitoring"
        elif any(word in text_lower for word in ["consult", "appointment", "medication", "therapy"]):
            return "medical"
        else:
            return "medical"
    
    def _deduplicate_recommendations(
        self,
        recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """Remove duplicate recommendations, keeping highest priority."""
        
        seen = {}
        result = []
        
        for rec in recommendations:
            key = rec.text.strip().lower()
            if key not in seen:
                seen[key] = rec
                result.append(rec)
            else:
                # Keep higher priority (lower number)
                if rec.priority < seen[key].priority:
                    result.remove(seen[key])
                    seen[key] = rec
                    result.append(rec)
        
        return result
    
    def get_recommendation_summary(
        self,
        recommendations: List[Recommendation]
    ) -> Dict[str, int]:
        """
        Summarize recommendations by category.
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Dict: Category counts
        """
        
        summary = {
            "urgent": 0,
            "medical": 0,
            "monitoring": 0,
            "lifestyle": 0,
            "testing": 0
        }
        
        for rec in recommendations:
            summary[rec.category] = summary.get(rec.category, 0) + 1
        
        return summary


def generate_recommendations(
    urgency_level: UrgencyLevel,
    abnormal_parameters: Dict[str, dict],
    age: Optional[int] = None,
    gender: Optional[str] = None,
    medical_history: Optional[List[str]] = None,
    max_recommendations: int = 10
) -> List[Recommendation]:
    """Convenience function for quick recommendation generation."""
    engine = RecommendationEngine()
    return engine.generate_recommendations(
        urgency_level=urgency_level,
        abnormal_parameters=abnormal_parameters,
        age=age,
        gender=gender,
        medical_history=medical_history,
        max_recommendations=max_recommendations
    )


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    engine = RecommendationEngine()
    
    abnormal_params = {
        "glucose": {"value": 250, "severity": "high"},
        "cholesterol": {"value": 220, "severity": "high"},
        "hdl": {"value": 30, "severity": "high"}
    }
    
    recommendations = engine.generate_recommendations(
        urgency_level=UrgencyLevel.HIGH,
        abnormal_parameters=abnormal_params,
        age=58,
        gender="Male",
        medical_history=["Type 2 Diabetes", "Hypertension"]
    )
    
    print("\n=== Recommendations ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec.category.upper()}] {rec.text}")
        print(f"   Priority: {rec.priority}, Urgency: {rec.urgency.value}")
    
    # Summary
    summary = engine.get_recommendation_summary(recommendations)
    print(f"\nSummary: {summary}")
