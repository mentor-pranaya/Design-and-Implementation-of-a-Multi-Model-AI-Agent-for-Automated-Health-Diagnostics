"""
Diet Recommendation Module - Phase 3
Specializes in dietary guidance based on detected conditions.
"""

from typing import List, Dict, Any
import json
from pathlib import Path
import os


class DietRecommendationModule:
    """
    Specialized module for diet-specific recommendations.
    Provides detailed nutritional guidance based on medical conditions.
    """
    
    def __init__(self, food_guidelines_path: str = None):
        """
        Initialize diet recommendation module.
        
        Args:
            food_guidelines_path: Path to food_guidelines.json
        """
        if food_guidelines_path is None:
            script_dir = Path(__file__).parent.parent
            food_guidelines_path = os.path.join(script_dir, 'knowledge_base', 'food_guidelines.json')
        
        self.food_guidelines = self._load_food_guidelines(food_guidelines_path)
    
    def _load_food_guidelines(self, path: str) -> Dict[str, Any]:
        """Load food guidelines from JSON."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load food guidelines: {e}")
            return {}
    
    def get_diet_recommendations(self, condition: str) -> Dict[str, List[str]]:
        """
        Get detailed diet recommendations for a condition.
        
        Args:
            condition: Name of the medical condition
            
        Returns:
            Dictionary with dietary recommendations, food lists, and tips
        """
        recommendations = {}
        
        # Map conditions to relevant food guidelines
        condition_to_guidelines = {
            "Anemia Indicator": ["iron_rich_foods"],
            "High Cholesterol": ["cholesterol_reducing_foods"],
            "Low Cholesterol": ["general_healthy_eating"],
            "Thyroid Disorder": ["thyroid_health"],
            "High Blood Pressure": ["heart_healthy_foods"],
            "Low Blood Pressure": ["general_healthy_eating"],
            "Elevated Blood Sugar": ["blood_sugar_regulation"],
            "Metabolic Syndrome Indicator": ["cholesterol_reducing_foods", "blood_sugar_regulation"],
            "Elevated Liver Enzymes": ["liver_health"],
            "Elevated Kidney Parameters": ["kidney_health"],
        }
        
        guideline_keys = condition_to_guidelines.get(condition, ["general_healthy_eating"])
        
        for key in guideline_keys:
            if key in self.food_guidelines:
                recommendations.update(self.food_guidelines[key])
        
        if not recommendations:
            recommendations = self.food_guidelines.get("general_healthy_eating", {})
        
        return recommendations
    
    def get_meal_planning_tips(self, conditions: List[str]) -> Dict[str, Any]:
        """
        Get meal planning tips for multiple conditions.
        
        Args:
            conditions: List of detected conditions
            
        Returns:
            Meal planning strategies and tips
        """
        return {
            "meal_timing": [
                "Eat at regular times to maintain stable metabolism",
                "Space meals 3-4 hours apart",
                "Don't skip breakfast",
                "Eat smaller portions more frequently if needed"
            ],
            "portion_control": [
                "Use smaller plates to control portions",
                "Fill half plate with vegetables",
                "Include palm-sized protein portion",
                "Add carbohydrate portion (fist-sized or smaller for blood sugar concerns)"
            ],
            "food_preparation": [
                "Prepare meals at home to control ingredients",
                "Use cooking methods: boil, bake, grill, steam (avoid frying)",
                "Season with herbs and spices instead of salt",
                "Batch cook for consistency throughout the week"
            ],
            "shopping_tips": [
                "Shop the perimeter of grocery store (fresh foods)",
                "Read nutrition labels carefully",
                "Choose whole grain products",
                "Buy fresh seasonal produce when possible",
                "Limit processed and packaged foods"
            ]
        }


if __name__ == "__main__":
    diet_module = DietRecommendationModule()
    
    # Example usage
    print("Diet Recommendations for Anemia:")
    anemia_diet = diet_module.get_diet_recommendations("Anemia Indicator")
    for category, items in anemia_diet.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for item in items:
            print(f"  • {item}")
    
    print("\n\nMeal Planning Tips:")
    tips = diet_module.get_meal_planning_tips(["Anemia Indicator"])
    for category, tip_list in tips.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for tip in tip_list:
            print(f"  • {tip}")
