from utils.reference_ranges import REFERENCE_RANGES

def detect_borderline_parameters(model1_results, margin=0.05):
    """
    Detects parameters that are close to abnormal limits.
    margin = 5% by default
    """

    borderline_notes = []

    for param, result in model1_results.items():
        if param not in REFERENCE_RANGES:
            continue

        value = result["value"]
        low, high = REFERENCE_RANGES[param]

        lower_margin = low + (low * margin)
        upper_margin = high - (high * margin)

        if low <= value <= lower_margin:
            borderline_notes.append(
                f"{param.replace('_',' ').title()} is near the lower normal limit"
            )

        elif upper_margin <= value <= high:
            borderline_notes.append(
                f"{param.replace('_',' ').title()} is near the upper normal limit"
            )

    return borderline_notes
