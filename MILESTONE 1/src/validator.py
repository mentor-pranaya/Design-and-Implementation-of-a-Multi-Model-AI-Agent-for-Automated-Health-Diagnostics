def standardize_data(data):
    """
    Normalizes units and values for consistency across different lab standards.
    Example: Converts Glucose from mmol/L to mg/dL.
    """
    for item in data:
        # Use .lower() to ensure matching is case-insensitive
        param = item.get('parameter', '').lower()
        unit = item.get('unit', '').lower()
        val = item.get('value')

        # Skip if there's no numerical value to process
        if val is None:
            continue

        # 1. Glucose: mmol/L to mg/dL (Factor: 18.01)
        if "glucose" in param and "mmol" in unit:
            item['value'] = round(val * 18.01, 2)
            item['unit'] = "mg/dL"
            item['range'] = "70-99"

        # 2. Cholesterol: mmol/L to mg/dL (Factor: 38.67)
        elif ("cholesterol" in param or "ldl" in param or "hdl" in param) and "mmol" in unit:
            item['value'] = round(val * 38.67, 2)
            item['unit'] = "mg/dL"
            # Note: Specific ranges are usually set in the interpreter

        # 3. Hemoglobin: g/L to g/dL (Factor: 0.1)
        elif "hemoglobin" in param and unit == "g/l":
            item['value'] = round(val / 10, 1)
            item['unit'] = "g/dL"

        # 4. Cleanup: Ensure unit string is consistently formatted
        if item.get('unit'):
            # Standardize common unit strings for display
            item['unit'] = item['unit'].replace("mmoll", "mmol/L").replace("mgdl", "mg/dL")

    return data
