def interpret_parameters(parameters: dict):
    """
    Classifies blood parameters as Low / Normal / High
    based on standard reference ranges.
    """

    reference_ranges = {
        "Hemoglobin": (13.0, 17.0),           # g/dL (male)
        "Cholesterol": (0, 200),              # mg/dL
        "Triglyceride": (0, 150),              # mg/dL
        "Fasting Blood Sugar": (74, 106),      # mg/dL
        "HbA1c": (0, 5.7)                      # %
    }

    interpretation = {}

    for param, value in parameters.items():
        if param not in reference_ranges:
            interpretation[param] = "Unknown"
            continue

        low, high = reference_ranges[param]

        if value < low:
            interpretation[param] = "Low"
        elif value > high:
            interpretation[param] = "High"
        else:
            interpretation[param] = "Normal"

    return interpretation
