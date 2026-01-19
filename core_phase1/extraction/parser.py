import re


class ExtractionError(Exception):
    """Custom exception for extraction-related errors."""
    pass


VALUE_UNIT_PATTERN = re.compile(
    r"""
    (?P<value>-?\d+(\.\d+)?)      # numeric value (int or float)
    \s*
    (?P<unit>[a-zA-Z/%]+)?        # optional unit
    """,
    re.VERBOSE,
)


def parse_value_unit(raw_value: str) -> dict:
    """
    Parse numeric value and unit from raw string.

    Args:
        raw_value (str): e.g., "13.2 g/dL"

    Returns:
        dict: {"value": float, "unit": str or None}

    Raises:
        ExtractionError: if parsing fails
    """
    if not raw_value or not isinstance(raw_value, str):
        raise ExtractionError("Raw value must be a non-empty string")

    match = VALUE_UNIT_PATTERN.search(raw_value)

    if not match:
        raise ExtractionError(f"Could not parse value/unit from '{raw_value}'")

    value = float(match.group("value"))
    unit = match.group("unit")

    return {
        "value": value,
        "unit": unit,
    }


def extract_parameters(raw_data: dict) -> dict:
    """
    Extract value and unit for each parameter.

    Args:
        raw_data (dict): {parameter_name: raw_value_string}

    Returns:
        dict: {parameter_name: {"value": float, "unit": str}}
    """
    extracted =
