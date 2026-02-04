"""
Exercise Recommendation Module - Phase 3
Specializes in physical activity guidance based on detected conditions.
"""

from typing import List, Dict, Any


class ExerciseRecommendationModule:
    """
    Specialized module for exercise-specific recommendations.
    Provides detailed physical activity guidance based on medical conditions.
    """
    
    def __init__(self):
        """Initialize exercise recommendation module."""
        self.intensity_levels = {
            "light": "Low intensity, minimal elevation in heart rate",
            "moderate": "Able to talk but not sing during activity",
            "vigorous": "Can only speak a few words during activity"
        }
    
    def get_exercise_recommendations(self, condition: str, severity: str = "Moderate") -> Dict[str, Any]:
        """
        Get detailed exercise recommendations for a condition.
        
        Args:
            condition: Name of the medical condition
            severity: Severity level (Mild, Moderate, Severe)
            
        Returns:
            Dictionary with exercise recommendations and activity guidelines
        """
        # Adjust intensity based on severity
        intensity_map = {
            "Mild": "light",
            "Moderate": "moderate",
            "Severe": "light"
        }
        
        intensity = intensity_map.get(severity, "moderate")
        
        recommendations = {
            "intensity_level": self.intensity_levels.get(intensity, ""),
            "frequency": self._get_frequency(condition, severity),
            "duration": self._get_duration(condition, severity),
            "types": self._get_activity_types(condition),
            "precautions": self._get_precautions(condition),
            "progression": self._get_progression_plan(condition, severity)
        }
        
        return recommendations
    
    def _get_frequency(self, condition: str, severity: str) -> Dict[str, Any]:
        """Get recommended exercise frequency."""
        frequency_map = {
            "Anemia Indicator": {"Mild": "5 days/week", "Moderate": "3-4 days/week", "Severe": "2-3 days/week"},
            "High Cholesterol": {"Mild": "5-6 days/week", "Moderate": "4-5 days/week", "Severe": "3-4 days/week"},
            "Thyroid Disorder": {"Mild": "4-5 days/week", "Moderate": "3-4 days/week", "Severe": "2-3 days/week"},
            "Metabolic Syndrome Indicator": {"Mild": "5-6 days/week", "Moderate": "4-5 days/week", "Severe": "3-4 days/week"},
            "Elevated Blood Sugar": {"Mild": "5-7 days/week", "Moderate": "5-6 days/week", "Severe": "4-5 days/week"},
            "High Blood Pressure": {"Mild": "5-7 days/week", "Moderate": "4-5 days/week", "Severe": "3-4 days/week"},
            "Low Blood Pressure": {"Mild": "2-3 days/week", "Moderate": "2-3 days/week", "Severe": "1-2 days/week"},
            "Elevated Liver Enzymes": {"Mild": "4-5 days/week", "Moderate": "3-4 days/week", "Severe": "2-3 days/week"},
        }
        
        freq = frequency_map.get(condition, {}).get(severity, "3-4 days/week")
        return {
            "recommended": freq,
            "rest_days": "At least 1-2 days per week for recovery",
            "consistency": "More important than intensity"
        }
    
    def _get_duration(self, condition: str, severity: str) -> Dict[str, Any]:
        """Get recommended exercise duration."""
        duration_map = {
            "Anemia Indicator": {"Mild": "30-45 min", "Moderate": "20-30 min", "Severe": "10-20 min"},
            "High Cholesterol": {"Mild": "45-60 min", "Moderate": "30-45 min", "Severe": "20-30 min"},
            "Thyroid Disorder": {"Mild": "30-45 min", "Moderate": "20-30 min", "Severe": "15-20 min"},
            "Metabolic Syndrome Indicator": {"Mild": "45-60 min", "Moderate": "30-45 min", "Severe": "20-30 min"},
            "Elevated Blood Sugar": {"Mild": "45-60 min", "Moderate": "30-45 min", "Severe": "20-30 min"},
            "High Blood Pressure": {"Mild": "40-60 min", "Moderate": "30-45 min", "Severe": "20-30 min"},
            "Low Blood Pressure": {"Mild": "20-30 min", "Moderate": "15-20 min", "Severe": "10-15 min"},
            "Elevated Liver Enzymes": {"Mild": "30-45 min", "Moderate": "20-30 min", "Severe": "15-20 min"},
        }
        
        dur = duration_map.get(condition, {}).get(severity, "30 min")
        return {
            "recommended": dur,
            "note": "Can be split into 10-15 min sessions if needed",
            "warm_up": "5-10 minutes at start",
            "cool_down": "5-10 minutes at end"
        }
    
    def _get_activity_types(self, condition: str) -> List[str]:
        """Get recommended activity types for condition."""
        activity_map = {
            "Anemia Indicator": [
                "Light walking",
                "Gentle yoga",
                "Swimming",
                "Tai Chi",
                "Light cycling (stationary preferred)"
            ],
            "High Cholesterol": [
                "Brisk walking",
                "Jogging",
                "Cycling",
                "Swimming",
                "Elliptical trainer",
                "Dancing"
            ],
            "Thyroid Disorder": [
                "Walking",
                "Swimming",
                "Yoga",
                "Pilates",
                "Moderate cycling",
                "Light hiking"
            ],
            "Metabolic Syndrome Indicator": [
                "Brisk walking",
                "Jogging",
                "Cycling",
                "Swimming",
                "Resistance training",
                "Group fitness classes"
            ],
            "Elevated Blood Sugar": [
                "Brisk walking",
                "Jogging",
                "Cycling",
                "Swimming",
                "Dancing",
                "Team sports",
                "Resistance training"
            ],
            "High Blood Pressure": [
                "Brisk walking",
                "Jogging",
                "Cycling",
                "Swimming",
                "Aerobic classes",
                "Resistance training"
            ],
            "Low Blood Pressure": [
                "Gentle walking",
                "Stretching",
                "Yoga",
                "Tai Chi",
                "Light resistance training",
                "Swimming"
            ],
        }
        
        return activity_map.get(condition, [
            "Walking",
            "Swimming",
            "Cycling",
            "Yoga",
            "Tai Chi"
        ])
    
    def _get_precautions(self, condition: str) -> List[str]:
        """Get exercise precautions for condition."""
        precautions_map = {
            "Anemia Indicator": [
                "Avoid sudden movements or position changes",
                "Stop if dizziness or shortness of breath occurs",
                "Stay well-hydrated",
                "Exercise in well-ventilated areas",
                "Avoid exercising when feeling particularly fatigued"
            ],
            "High Cholesterol": [
                "Avoid extremely heavy weightlifting",
                "Warm up and cool down properly",
                "Monitor for chest discomfort",
                "Stay hydrated"
            ],
            "Thyroid Disorder": [
                "Avoid overexertion",
                "Monitor energy levels",
                "Rest adequately between sessions",
                "Avoid exercise if experiencing thyroid medication side effects"
            ],
            "Metabolic Syndrome Indicator": [
                "Monitor blood pressure during exercise",
                "Stay hydrated",
                "Warm up and cool down properly",
                "Exercise at consistent times",
                "Avoid extreme temperatures"
            ],
            "Elevated Blood Sugar": [
                "Check blood sugar before and after exercise",
                "Carry quick-acting carbs (juice, glucose tablets)",
                "Stay well-hydrated",
                "Wear comfortable shoes",
                "Monitor for signs of hypoglycemia"
            ],
            "High Blood Pressure": [
                "Avoid isometric exercises (holding heavy weights)",
                "Monitor blood pressure regularly",
                "Avoid sudden intense exertion",
                "Warm up and cool down gradually",
                "Breathe continuously (avoid holding breath)"
            ],
            "Low Blood Pressure": [
                "Avoid sudden position changes",
                "Rise slowly from lying or sitting",
                "Stay well-hydrated",
                "Avoid overheating",
                "Exercise in cooler environments"
            ],
        }
        
        return precautions_map.get(condition, [
            "Warm up before exercise",
            "Cool down after exercise",
            "Stay well-hydrated",
            "Listen to your body"
        ])
    
    def _get_progression_plan(self, condition: str, severity: str) -> Dict[str, List[str]]:
        """Get progressive exercise plan."""
        return {
            "week_1_to_2": [
                "Establish consistent schedule",
                "Focus on comfort and sustainability",
                "Build baseline fitness level",
                "Monitor how body responds"
            ],
            "week_3_to_4": [
                "Gradually increase duration by 5-10 minutes",
                "Introduce variety in activities",
                "Maintain consistency",
                "Assess energy and recovery"
            ],
            "week_5_to_8": [
                "Increase intensity slightly if tolerated",
                "Add strength training if appropriate",
                "Maintain progress with variety",
                "Re-evaluate after 8 weeks with healthcare provider"
            ],
            "month_3_plus": [
                "Maintain achieved fitness level",
                "Continue progressive overload if tolerated",
                "Incorporate new activities to prevent boredom",
                "Regular health monitoring and provider consultation"
            ]
        }


if __name__ == "__main__":
    exercise_module = ExerciseRecommendationModule()
    
    # Example usage
    print("Exercise Recommendations for Anemia Indicator (Mild):")
    recommendations = exercise_module.get_exercise_recommendations("Anemia Indicator", "Mild")
    
    for key, value in recommendations.items():
        print(f"\n{key.replace('_', ' ').title()}:")
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                print(f"  {sub_key.replace('_', ' ').title()}: {sub_value}")
        elif isinstance(value, list):
            for item in value:
                print(f"  • {item}")
        else:
            print(f"  {value}")
