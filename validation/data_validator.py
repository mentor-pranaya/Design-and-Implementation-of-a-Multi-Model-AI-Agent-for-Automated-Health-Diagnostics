def validate_value(value):
    if value is None:
        return None
    try:
        return float(value)
    except:
        return None
