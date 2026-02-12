def clean_and_structure_data(params: dict) -> dict:
    # Normalize keys and values, remove invalid entries
    cleaned = {}
    for key, value in params.items():
        key = key.lower().strip()
        if isinstance(value, (int, float)) and 0 <= value <= 10000:  # Basic range check
            cleaned[key] = value
    return cleaned