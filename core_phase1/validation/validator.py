class ValidationError(Exception):
    """Custom exception for validation-related issues."""
    pass


# Simple unit whitelist (expand later if needed)
ALLOWED_UNITS = {
    "g/dL",
    "mg/dL",
    "%",
}


def validate_parameters(extracted_data: dict) -> dict:
    """
    Validate extracted parameters for plausibility and unit correctness.

    Args:
        extracted_data (dict): Output from extraction stage

    Returns:
        dict: Validated parameters with flags and warnings
    """
    validated = {}

    for parameter, details in extracted_data.items():
        value = details.get("value")
        unit = details.get("unit")

        param_result = {
            "value": value,
            "unit": unit,
            "valid": True,
            "warnings": [],
        }

        # Missing value
        if value is None:
            param_result["valid"] = False
            param_result["warnings"].append("Missing numeric value")

        # Negative values (biologically implausible)
        elif value < 0:
            param_result["valid"] = False
            param_result["warnings"].append("Negative value detected")

        # Unit validation
        if unit and unit not in ALLOWED_UNITS:
            param_result["warnings"].append(f"Unrecognized unit '{unit}'")

        validated[parameter]()
