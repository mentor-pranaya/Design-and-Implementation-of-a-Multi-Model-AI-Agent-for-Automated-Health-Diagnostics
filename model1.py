REFERENCE = {
    "Hemoglobin": {
        "range": (12, 16),
        "unit": "g/dL",
        "note": "Oxygen-carrying protein in blood"
    },
    "Total WBC Count": {
        "range": (4000, 11000),
        "unit": "/cumm",
        "note": "White blood cells responsible for immunity"
    },
    "Platelet Count": {
        "range": (1.5, 4.1),
        "unit": "lakhs/cumm",
        "note": "Blood cells responsible for clotting"
    },
    "RBC Count": {
        "range": (4.5, 5.5),
        "unit": "million/cumm",
        "note": "Red blood cells that carry oxygen"
    },
    "MCV": {
        "range": (83, 101),
        "unit": "fL",
        "note": "Average size of red blood cells"
    },
    "MCHC": {
        "range": (31.5, 34.5),
        "unit": "%",
        "note": "Hemoglobin concentration in RBCs"
    }
}


def normalize_value(test, value):
    if value is None:
        return None
    if test == "Total WBC Count" and value < 100:
        return value * 1000
    return value


def interpret(test, value):
    if test not in REFERENCE or value is None:
        return "Unknown"

    low, high = REFERENCE[test]["range"]
    if value < low:
        return "Low"
    elif value > high:
        return "High"
    else:
        return "Normal"
