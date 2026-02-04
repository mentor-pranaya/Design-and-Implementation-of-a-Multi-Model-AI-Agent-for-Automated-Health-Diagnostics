"""
Lifestyle Recommendation Module - Phase 3
Specializes in overall lifestyle and behavioral guidance based on detected conditions.
"""

from typing import List, Dict, Any


class LifestyleRecommendationModule:
    """
    Specialized module for lifestyle-specific recommendations.
    Provides guidance on sleep, stress management, habits, and behavioral changes.
    """
    
    def __init__(self):
        """Initialize lifestyle recommendation module."""
        pass
    
    def get_lifestyle_recommendations(self, condition: str) -> Dict[str, Any]:
        """
        Get comprehensive lifestyle recommendations for a condition.
        
        Args:
            condition: Name of the medical condition
            
        Returns:
            Dictionary with lifestyle recommendations across multiple categories
        """
        return {
            "sleep": self._get_sleep_recommendations(condition),
            "stress_management": self._get_stress_recommendations(condition),
            "habits": self._get_habit_recommendations(condition),
            "environmental": self._get_environmental_recommendations(condition),
            "monitoring": self._get_monitoring_recommendations(condition)
        }
    
    def _get_sleep_recommendations(self, condition: str) -> Dict[str, Any]:
        """Get sleep-specific recommendations."""
        sleep_map = {
            "Anemia Indicator": {
                "duration": "8-9 hours nightly",
                "tips": [
                    "Sleep is crucial for red blood cell production",
                    "Maintain consistent sleep schedule (even on weekends)",
                    "Rest adequately between activities",
                    "Create dark, cool, quiet sleep environment",
                    "Avoid caffeine 4-6 hours before bedtime"
                ]
            },
            "High Cholesterol": {
                "duration": "7-8 hours nightly",
                "tips": [
                    "Poor sleep increases cardiovascular risk",
                    "Consistent sleep schedule supports heart health",
                    "Avoid heavy meals 2-3 hours before sleep",
                    "Limit screen time before bed",
                    "Exercise earlier in the day, not close to bedtime"
                ]
            },
            "Thyroid Disorder": {
                "duration": "7-8 hours nightly",
                "tips": [
                    "Sleep regulation is important for thyroid function",
                    "Maintain consistent sleep-wake schedule",
                    "Bedroom temperature should be cool (65-68°F)",
                    "Avoid stimulating activities before bed",
                    "Take thyroid medication on empty stomach as prescribed"
                ]
            },
            "Metabolic Syndrome Indicator": {
                "duration": "7-9 hours nightly",
                "tips": [
                    "Poor sleep worsens metabolic disorders",
                    "Regular sleep schedule improves insulin sensitivity",
                    "Sleep apnea screening recommended",
                    "Avoid alcohol which disrupts sleep quality",
                    "Create consistent bedtime routine"
                ]
            },
            "Elevated Blood Sugar": {
                "duration": "7-9 hours nightly",
                "tips": [
                    "Good sleep improves glucose control",
                    "Consistent sleep schedule is critical",
                    "Avoid sugary snacks before bed",
                    "Sleep apnea is common in diabetes; get screened",
                    "Maintain consistent meal and sleep timing"
                ]
            },
            "High Blood Pressure": {
                "duration": "7-8 hours nightly",
                "tips": [
                    "Good sleep lowers blood pressure",
                    "Consistent schedule supports blood pressure control",
                    "Sleep apnea increases hypertension risk",
                    "Avoid alcohol before bedtime",
                    "Keep bedroom cool and quiet"
                ]
            },
            "Low Blood Pressure": {
                "duration": "8-9 hours nightly",
                "tips": [
                    "Adequate sleep helps maintain stable blood pressure",
                    "Rise slowly when waking to avoid dizziness",
                    "Stay hydrated before and after sleep",
                    "Elevate head slightly while sleeping",
                    "Avoid caffeine as it may worsen symptoms"
                ]
            },
        }
        
        default = {
            "duration": "7-8 hours nightly",
            "tips": [
                "Maintain consistent sleep schedule",
                "Create dark, cool, quiet sleep environment",
                "Avoid screens 30-60 minutes before bed",
                "Limit caffeine, especially afternoon/evening",
                "Avoid large meals before bedtime"
            ]
        }
        
        return sleep_map.get(condition, default)
    
    def _get_stress_recommendations(self, condition: str) -> Dict[str, Any]:
        """Get stress management recommendations."""
        return {
            "daily_practices": [
                "Meditation or mindfulness: 10-15 minutes daily",
                "Deep breathing exercises: 5 minutes, 2-3 times daily",
                "Progressive muscle relaxation: 15-20 minutes",
                "Journaling: 10 minutes to process emotions",
                "Gratitude practice: identify 3 things daily"
            ],
            "condition_specific": self._get_condition_stress_notes(condition),
            "activities": [
                "Nature walks or time in parks",
                "Creative pursuits (art, music, writing)",
                "Social connection with friends/family",
                "Pet companionship and care",
                "Hobbies and leisure activities"
            ],
            "warning_signs": [
                "Increased anxiety or depression",
                "Sleep disruption or insomnia",
                "Appetite changes",
                "Difficulty concentrating",
                "Increased symptom severity with stress"
            ]
        }
    
    def _get_condition_stress_notes(self, condition: str) -> List[str]:
        """Get condition-specific stress management notes."""
        stress_map = {
            "High Blood Pressure": [
                "Chronic stress significantly elevates blood pressure",
                "Regular stress reduction can lower BP by 5-10 mmHg",
                "Yoga or tai chi particularly beneficial"
            ],
            "Elevated Blood Sugar": [
                "Stress hormones increase blood glucose",
                "Stress management is crucial for diabetes prevention",
                "Maintain consistent routine during stressful periods"
            ],
            "Thyroid Disorder": [
                "Stress can trigger or worsen autoimmune thyroid disease",
                "Stress management reduces symptom flare-ups",
                "Support groups helpful for coping"
            ],
            "Metabolic Syndrome Indicator": [
                "Stress contributes to poor metabolic health",
                "Cortisol (stress hormone) increases belly fat",
                "Prioritize stress reduction alongside diet and exercise"
            ],
            "High Cholesterol": [
                "Stress increases cholesterol and triglycerides",
                "Stress reduction is complementary to medication",
                "Mind-body practices beneficial"
            ],
        }
        
        return stress_map.get(condition, [
            "Regular stress management supports overall health",
            "Identify personal stress triggers",
            "Develop coping strategies and support network"
        ])
    
    def _get_habit_recommendations(self, condition: str) -> Dict[str, List[str]]:
        """Get habit change recommendations."""
        return {
            "habits_to_adopt": [
                "Regular health monitoring (check vital signs)",
                "Consistent meal times and portion control",
                "Daily physical activity or movement",
                "Regular hydration throughout the day",
                "Medication adherence if prescribed",
                "Regular health checkups and screenings"
            ],
            "habits_to_avoid": [
                "Smoking and tobacco use",
                "Excessive alcohol consumption",
                "Prolonged sedentary behavior",
                "Skipping meals",
                "Emotional eating or stress eating",
                "Irregular sleep schedule",
                "Self-medication or over-the-counter medication misuse"
            ],
            "habit_change_tips": [
                "Start with one habit at a time",
                "Set specific, measurable goals",
                "Track progress daily or weekly",
                "Identify triggers and prepare alternatives",
                "Build habits gradually (gradual change is sustainable)",
                "Use positive reinforcement, not punishment",
                "Involve family for accountability and support",
                "Expect setbacks; get back on track immediately"
            ]
        }
    
    def _get_environmental_recommendations(self, condition: str) -> Dict[str, List[str]]:
        """Get environmental and contextual recommendations."""
        return {
            "home_environment": [
                "Keep healthy foods visible and accessible",
                "Remove tempting unhealthy foods from home",
                "Create a dedicated exercise space",
                "Maintain comfortable temperature for sleep",
                "Minimize noise and light disruptions",
                "Stock kitchen with cooking supplies for healthy meals"
            ],
            "work_environment": [
                "Take movement breaks every hour",
                "Use stairs instead of elevators",
                "Bring healthy snacks to work",
                "Stay hydrated with water throughout the day",
                "Set reminders for medication if needed",
                "Manage workplace stress through boundaries"
            ],
            "social_support": [
                "Inform family and friends about health goals",
                "Find accountability partner or health buddy",
                "Join support groups (online or in-person)",
                "Consider working with nutritionist or health coach",
                "Communicate needs to healthcare team",
                "Avoid peer pressure regarding unhealthy behaviors"
            ]
        }
    
    def _get_monitoring_recommendations(self, condition: str) -> Dict[str, Any]:
        """Get self-monitoring recommendations."""
        monitoring_map = {
            "Anemia Indicator": {
                "metrics": ["Hemoglobin levels", "Energy levels", "Shortness of breath"],
                "frequency": "Check hemoglobin every 6-8 weeks"
            },
            "High Cholesterol": {
                "metrics": ["Cholesterol levels", "Diet adherence", "Exercise frequency"],
                "frequency": "Lipid panel every 3-6 months"
            },
            "Thyroid Disorder": {
                "metrics": ["Energy levels", "Weight", "TSH levels"],
                "frequency": "TSH recheck every 6-8 weeks after medication change, then annually"
            },
            "Metabolic Syndrome Indicator": {
                "metrics": ["Fasting glucose", "Weight", "Waist circumference", "Blood pressure"],
                "frequency": "Metabolic panel every 3 months"
            },
            "Elevated Blood Sugar": {
                "metrics": ["Fasting glucose", "Post-meal glucose", "HbA1c"],
                "frequency": "Glucose monitoring 2-4 times daily (if diabetic), HbA1c every 3 months"
            },
            "High Blood Pressure": {
                "metrics": ["Blood pressure readings", "Sodium intake", "Exercise frequency"],
                "frequency": "Daily morning blood pressure monitoring recommended"
            },
            "Low Blood Pressure": {
                "metrics": ["Orthostatic symptoms", "Hydration status", "Weight"],
                "frequency": "Blood pressure monitoring in lying, sitting, and standing positions"
            },
        }
        
        default = {
            "metrics": ["Overall well-being", "Energy levels", "Symptom presence"],
            "frequency": "Regular self-assessment and annual health checkups"
        }
        
        return monitoring_map.get(condition, default)


if __name__ == "__main__":
    lifestyle_module = LifestyleRecommendationModule()
    
    # Example usage
    print("Lifestyle Recommendations for High Blood Pressure:")
    recommendations = lifestyle_module.get_lifestyle_recommendations("High Blood Pressure")
    
    for category, content in recommendations.items():
        print(f"\n{category.replace('_', ' ').upper()}:")
        if isinstance(content, dict):
            for key, value in content.items():
                print(f"\n  {key.replace('_', ' ').title()}:")
                if isinstance(value, list):
                    for item in value:
                        print(f"    • {item}")
                else:
                    print(f"    {value}")
        elif isinstance(content, list):
            for item in content:
                print(f"  • {item}")
