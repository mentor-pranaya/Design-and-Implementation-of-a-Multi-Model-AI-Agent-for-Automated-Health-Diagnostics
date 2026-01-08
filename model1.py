from reference_ranges import REFERENCE_RANGES

def interpret(parameters):
    results = {}

    for param, value in parameters.items():
        low, high = REFERENCE_RANGES[param]

        if value < low:
            results[param] = "LOW"
        elif value > high:
            results[param] = "HIGH"
        else:
            results[param] = "NORMAL"

    return results
