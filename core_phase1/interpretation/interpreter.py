from interpretation.reference_ranges import REFERENCE_RANGES


def interpret_parameters(validated_data: dict) -> dict:
    """
    Classify parameters as Low / Normal / High based on reference ranges.

    Args:
        validated_data (dict): Output from validation stage

    Returns:
        dict: Interpreted parameters with status
    """
    interpreted = {}

    for parameter, details in validated_data.items():
        value = details.get("value")
        unit = details.get("unit")
        valid = details.get("valid")

        result = {
            "value": value,
            "unit": unit,
            "status": "Unknown",
            "reference_range": None,
            "warnings": details.get("warnings", []),
        }

        if not valid:
            result["status"] = "Invalid"
            interpreted[parameter] = result
            continue

        if parameter not in REFERENCE_RANGES:
            result["warnings"].append("No reference range available")
            interpreted[parameter] = result
            continue

        ref = REFERENCE_RANGES[parameter]

        # Unit mismatch warning
        if unit != ref["unit"]:
            result["warnings"].append(
                f"Unit mismatch: expected {ref['unit']}, got {unit}"
            )

        low = ref["low"]
        high = ref["high"]

        if value < low:
            result["status"] = "Low"
        elif value > high:
            result["status"] = "High"
        else:
            result["status"] = "Normal"

        result["reference_range"] = f"{low}–{high} {ref['unit']}"
        interpreted[parameter] = result

    return interpreted
