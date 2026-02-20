# model_1/reference_ranges.py

REFERENCE_RANGES = {

    # --------------------
    # Glucose & Lipids
    # --------------------
    "glucose_fasting": {
        "unit": "mg/dL",
        "ranges": {
            "normal": (70, 99),
            "pre_high": (100, 125),
            "high": (126, float("inf"))
        }
    },

    "hdl": {
        "unit": "mg/dL",
        "ranges": {
            "low": (0, 39),
            "normal": (40, float("inf"))
        }
    },

    "ldl": {
        "unit": "mg/dL",
        "ranges": {
            "normal": (0, 99),
            "borderline": (100, 129),
            "high": (130, float("inf"))
        }
    },

    "total_cholesterol": {
        "unit": "mg/dL",
        "ranges": {
            "normal": (0, 199),
            "borderline": (200, 239),
            "high": (240, float("inf"))
        }
    },

    # --------------------
    # CBC PARAMETERS
    # --------------------
    "hemoglobin": {
        "unit": "g/dL",
        "by_gender": {
            "male": {
                "low": (0, 13.0),
                "normal": (13.0, 17.5),
                "high": (17.6, float("inf"))
            },
            "female": {
                "low": (0, 12.0),
                "normal": (12.0, 15.0),
                "high": (15.1, float("inf"))
            }
        }
    },

    "rbc": {
        "unit": "million/uL",
        "by_gender": {
            "male": {
                "low": (0, 4.5),
                "normal": (4.5, 6.0),
                "high": (6.1, float("inf"))
            },
            "female": {
                "low": (0, 3.9),
                "normal": (3.9, 5.6),
                "high": (5.7, float("inf"))
            }
        }
    },

    "wbc": {
        "unit": "cells/uL",
        "ranges": {
            "low": (0, 4000),
            "normal": (4000, 11000),
            "high": (11001, float("inf"))
        }
    },

    "platelets": {
        "unit": "cells/uL",
        "ranges": {
            "low": (0, 150000),
            "normal": (150000, 450000),
            "high": (450001, float("inf"))
        }
    },

    # --------------------
    # BLOOD PRESSURE
    # --------------------
    "bp_systolic": {
        "unit": "mmHg",
        "ranges": {
            "normal": (90, 120),
            "elevated": (121, 129),
            "high": (130, float("inf"))
        }
    },

    "bp_diastolic": {
        "unit": "mmHg",
        "ranges": {
            "normal": (60, 80),
            "high": (81, float("inf"))
        }
    }
}
