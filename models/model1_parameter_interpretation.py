from utils.reference_ranges import REFERENCE_RANGES


def interpret_parameters(extracted_parameters):
    """
    Model-1: Parameter Interpretation

    Input:
    extracted_parameters = {
        "hemoglobin": 9.5,
        "mcv": 75,
        "wbc_count": 12000
    }

    Output:
    model1_results = {
        "hemoglobin": {"value": 9.5, "status": "Low"},
        "mcv": {"value": 75, "status": "Low"},
        "wbc_count": {"value": 12000, "status": "High"}
    }
    """

    model1_results = {}

    for parameter, value in extracted_parameters.items():

        # If reference range is missing
        if parameter not in REFERENCE_RANGES:
            model1_results[parameter] = {
                "value": value,
                "status": "Unknown"
            }
            continue

        low, high = REFERENCE_RANGES[parameter]

        if value < low:
            status = "Low"
        elif value > high:
            status = "High"
        else:
            status = "Normal"

        model1_results[parameter] = {
            "value": value,
            "status": status
        }

    return model1_results

