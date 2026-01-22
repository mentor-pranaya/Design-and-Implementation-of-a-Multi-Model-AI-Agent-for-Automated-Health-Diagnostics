def classify_parameters(validated_data: dict) -> dict:
    """
    Classify validated parameters into clinical categories.

    Args:
        validated_data (dict): Output from validator

    Returns:
        dict: Interpreted clinical status
    """
    interpreted = {}

    for parameter, details in validated_data.items():
        severity = details.get("severity", "Unknown")
        value = details.get("value")

        interpretation = {
            "value": value,
            "status": severity,
            "clinical_note": ""
        }

        if severity == "Low":
            interpretation["clinical_note"] = f"{parameter} is below normal range"
        elif severity == "High":
            interpretation["clinical_note"] = f"{parameter} is above normal range"
        elif severity == "Normal":
            interpretation["clinical_note"] = f"{parameter} is within normal range"
        else:
            interpretation["clinical_note"] = f"{parameter} could not be evaluated"

        interpreted[parameter] = interpretation

    return interpreted
