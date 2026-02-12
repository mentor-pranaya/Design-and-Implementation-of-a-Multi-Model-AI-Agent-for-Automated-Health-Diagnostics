def validate_parameters(parameters: dict):
    """
    Validates extracted blood parameters.
    Removes invalid values and flags missing ones.
    """

    validated = {}
    issues = []

    for param, value in parameters.items():
        # Check type
        if not isinstance(value, (int, float)):
            issues.append(f"{param}: Invalid type")
            continue

        # Check value range (basic sanity)
        if value <= 0:
            issues.append(f"{param}: Invalid value ({value})")
            continue

        validated[param] = value

    if not validated:
        issues.append("No valid parameters found")

    return validated, issues
