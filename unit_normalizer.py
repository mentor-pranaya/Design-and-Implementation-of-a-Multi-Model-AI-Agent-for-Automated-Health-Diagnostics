def normalize_unit(test_name: str, raw_unit: str):
    """
    Normalize units into a standard form. Uses a lightweight mapper when available,
    otherwise falls back to defaults per test. Returns None if no mapping.
    """
    try:
        from model_1.unit_mapper import normalize_unit as map_unit
    except Exception:
        map_unit = None

    DEFAULT_UNITS = {
        "glucose_fasting": "mg/dL",
        "glucose_random": "mg/dL",
        "total_cholesterol": "mg/dL",
        "hdl": "mg/dL",
        "ldl": "mg/dL",
        "hemoglobin": "g/dL"
    }

    if raw_unit:
        if map_unit:
            try:
                return map_unit(raw_unit)
            except Exception:
                return raw_unit
        return raw_unit

    return DEFAULT_UNITS.get(test_name)
