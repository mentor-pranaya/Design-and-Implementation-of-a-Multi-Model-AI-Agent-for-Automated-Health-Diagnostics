def interpret(parameters):
    interpretation = {}

    ranges = {
        "Hemoglobin": (12, 17),
        "Glucose": (70, 110),
        "Cholesterol": (0, 200),
        "LDL": (0, 130),
        "HDL": (40, 100),
        "Triglycerides": (0, 150),
        "Creatinine": (0.6, 1.2),
        "WBC": (4.0, 11.0),
        "RBC": (4.0, 6.0),
        "Platelets": (150, 450)
    }

    for param, value in parameters.items():
        low, high = ranges.get(param, (0, float("inf")))

        if value < low:
            interpretation[param] = "LOW"
        elif value > high:
            interpretation[param] = "HIGH"
        else:
            interpretation[param] = "NORMAL"

    return interpretation
