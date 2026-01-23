def interpret(parameters):
    interpretation = {}

    ranges = {
        "Hemoglobin": (12, 17),
        "Glucose": (70, 110),
        "Cholesterol": (0, 200)
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
