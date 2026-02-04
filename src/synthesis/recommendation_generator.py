import json
import os
from src.config.reference_loader import get_age_group


class RecommendationGenerator:
   
    
    def __init__(self):
        self._load_recommendations()
    
    def _load_recommendations(self):
        """Load recommendations from JSON file"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "config", "recommendations.json")
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Recommendations file not found: {json_path}")
            self._data = {"conditions": {}, "general_advice": {}, "age_specific": {}, "gender_specific": {}}
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in recommendations file: {e}")
            self._data = {"conditions": {}, "general_advice": {}, "age_specific": {}, "gender_specific": {}}
    
    def _map_condition_to_key(self, condition_name):
        
        name_lower = condition_name.lower()
        
        if "iron deficiency" in name_lower:
            return "iron_deficiency"
        elif "anemia" in name_lower:
            return "anemia"
        elif "kidney" in name_lower:
            return "kidney_concern"
        elif "leukopenia" in name_lower or "low wbc" in name_lower:
            return "leukopenia"
        elif "infection" in name_lower or "inflammation" in name_lower:
            return "infection"
        elif "low rbc" in name_lower:
            return "low_rbc_only"
        else:
            return None
    
    def _get_condition_recommendations(self, condition_key, severity="mild"):
        
        conditions = self._data.get("conditions", {})
        condition_data = conditions.get(condition_key, {})
        
        if not condition_data:
            return None
        
        recommendations = {
            "condition_name": condition_data.get("name", condition_key),
            "description": condition_data.get("description", ""),
            "diet": condition_data.get("diet", []),
            "lifestyle": condition_data.get("lifestyle", []),
            "followup": condition_data.get("followup", []),
            "warnings": condition_data.get("warnings", []),
            "priority": "MEDIUM",
            "timeline": "4-6 weeks follow-up"
        }
        
        # Apply severity-specific modifications
        severity_data = condition_data.get("severity_specific", {}).get(severity, {})
        if severity_data:
            recommendations["priority"] = severity_data.get("priority", recommendations["priority"])
            recommendations["timeline"] = severity_data.get("timeline", recommendations["timeline"])
        
        return recommendations
    
    def _get_age_specific_advice(self, age):
        
        age_group = get_age_group(age)
        age_data = self._data.get("age_specific", {}).get(age_group, {})
        
        return {
            "notes": age_data.get("notes", ""),
            "diet_modifier": age_data.get("diet_modifier", "")
        }
    
    def _get_gender_specific_advice(self, gender):
       
        if not gender:
            return {"notes": ""}
        
        gender_data = self._data.get("gender_specific", {}).get(gender.lower(), {})
        
        return {
            "notes": gender_data.get("notes", "")
        }
    
    def generate(self, synthesis_result, age=None, gender=None):
       
        conditions = synthesis_result.get("conditions", [])
        risk_level = synthesis_result.get("risk_level", "MINIMAL RISK")
        
        all_recommendations = []
        
        # Generate recommendations for each condition
        for condition in conditions:
            condition_name = condition.get("name", "")
            severity = condition.get("severity", "mild")
            
            # Map to recommendation key
            rec_key = self._map_condition_to_key(condition_name)
            
            if rec_key:
                rec = self._get_condition_recommendations(rec_key, severity)
                if rec:
                    rec["linked_condition"] = condition_name
                    rec["confidence"] = condition.get("confidence", 0)
                    rec["indicators"] = condition.get("indicators", [])
                    all_recommendations.append(rec)
        
        # If no conditions, provide normal/general recommendations
        if not all_recommendations:
            normal_rec = self._get_condition_recommendations("normal")
            if normal_rec:
                normal_rec["linked_condition"] = "General Health Maintenance"
                normal_rec["confidence"] = 100
                normal_rec["indicators"] = ["All parameters within normal range"]
                all_recommendations.append(normal_rec)
        
        # Get age and gender specific advice
        age_advice = self._get_age_specific_advice(age)
        gender_advice = self._get_gender_specific_advice(gender)
        
        # Get general advice
        general_advice = self._data.get("general_advice", {})
        
        # Build final recommendation structure
        result = {
            "condition_recommendations": all_recommendations,
            "age_specific_advice": age_advice,
            "gender_specific_advice": gender_advice,
            "general_advice": general_advice,
            "overall_priority": self._determine_overall_priority(all_recommendations, risk_level),
            "summary": self._generate_recommendation_summary(all_recommendations, risk_level)
        }
        
        return result
    
    def _determine_overall_priority(self, recommendations, risk_level):
       
        priorities = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        
        max_priority = 1
        for rec in recommendations:
            priority = rec.get("priority", "LOW")
            max_priority = max(max_priority, priorities.get(priority, 1))
        
        # Also consider risk level
        if "HIGH" in risk_level:
            max_priority = max(max_priority, 3)
        elif "MODERATE" in risk_level:
            max_priority = max(max_priority, 2)
        
        priority_map = {3: "HIGH", 2: "MEDIUM", 1: "LOW"}
        return priority_map.get(max_priority, "LOW")
    
    def _generate_recommendation_summary(self, recommendations, risk_level):
        
        if not recommendations:
            return "Continue maintaining healthy lifestyle. No specific concerns identified."
        
        condition_names = [r.get("linked_condition", "Unknown") for r in recommendations]
        
        if "HIGH" in risk_level:
            return f"Based on your results, immediate attention is recommended for: {', '.join(condition_names)}. Please consult a healthcare provider promptly."
        elif "MODERATE" in risk_level:
            return f"Your results indicate concerns regarding: {', '.join(condition_names)}. Schedule a follow-up with your doctor within 2-4 weeks."
        elif "LOW" in risk_level:
            return f"Minor concerns identified: {', '.join(condition_names)}. Follow the dietary and lifestyle recommendations below. Retest in 4-6 weeks."
        else:
            return f"Your results are generally good. Consider the following recommendations for optimal health."


# Create singleton instance
_generator = None

def generate_recommendations(synthesis_result, age=None, gender=None):
    
    global _generator
    if _generator is None:
        _generator = RecommendationGenerator()
    
    return _generator.generate(synthesis_result, age, gender)