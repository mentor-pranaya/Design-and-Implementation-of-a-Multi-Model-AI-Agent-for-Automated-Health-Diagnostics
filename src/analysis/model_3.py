from typing import Dict, Any, Optional

class Model3:
    """
    Model 3: Contextual Analysis.
    Adjusts reference ranges and interpretations based on user context (age, gender, history).
    """

    def analyze(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Refine analysis based on patient context.
        Returns a dictionary with context-adjusted interpretations.
        """
        if not context:
            return {"context_adjustments": []}

        adjustments = []
        age = context.get("age")
        gender = context.get("gender", "unknown").lower()
        
        # example: Adjust Hemoglobin interpretation based on gender
        hb = parameters.get("Hemoglobin")
        if hb and isinstance(hb, dict):
            val = hb.get("value")
            if val is not None:
                # Female range is typically lower (12.0-15.5) vs Male (13.5-17.5)
                if gender in ["female", "f", "woman"]:
                    if val < 12.0:
                        adjustments.append("Hemoglobin is low for an adult female.")
                    elif val > 15.5:
                        adjustments.append("Hemoglobin is high for an adult female.")
                elif gender in ["male", "m", "man"]:
                     if val < 13.5:
                        adjustments.append("Hemoglobin is low for an adult male.")
                     elif val > 17.5:
                        adjustments.append("Hemoglobin is high for an adult male.")
        
        # Example: Adjust Creatinine interpretation based on gender
        creat = parameters.get("Creatinine")
        if creat and isinstance(creat, dict):
            val = creat.get("value")
            if val is not None:
                # Female: 0.5-1.1, Male: 0.6-1.2
                 if gender in ["female", "f", "woman"] and val > 1.1:
                      adjustments.append("Creatinine is slightly elevated for a female.")
                 elif gender in ["male", "m", "man"] and val > 1.2:
                      adjustments.append("Creatinine is elevated for a male.")

        # Example: Pediatric considerations (very simplified)
        if age and int(age) < 18:
            adjustments.append("Note: Pediatric reference ranges may differ significantly from adult norms used here.")

        return {
            "context_adjustments": adjustments,
            "applied_context": {
                "age": age,
                "gender": gender
            }
        }
