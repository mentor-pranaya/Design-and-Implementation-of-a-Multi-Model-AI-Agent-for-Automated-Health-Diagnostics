from utils.reference_ranges import REFERENCE_RANGES

def classify_parameter(parameter, value):
    low, high = REFERENCE_RANGES[parameter]

    if value < low:
        return "Low"
    elif value > high:
        return "High"
    else:
        return "Normal"
