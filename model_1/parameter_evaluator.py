# model_1/parameter_evaluator.py
from typing import Dict, Any, Optional


def evaluate_parameter(parameter_name: str, value, unit: Optional[str] = None,
                       parameter_definitions: Optional[Dict[str, Any]] = None,
                       age: Optional[int] = None, gender: Optional[str] = None):
    """Evaluate a single parameter using dataset-provided definitions.

    `parameter_definitions` is a mapping like the one returned by
    `model_1.dataset_loader.load_lab_report_ds()['parameters']`.
    If not provided, the function will attempt to fall back to the
    (legacy) `model_1.reference_ranges.REFERENCE_RANGES` for compatibility.
    """
    if parameter_definitions is None:
        try:
            from model_1.reference_ranges import REFERENCE_RANGES as parameter_definitions  # type: ignore
        except Exception:
            return {
                "status": "unknown",
                "reason": "No reference ranges or parameter definitions available"
            }

    # 1. Parameter exists?
    if parameter_name not in parameter_definitions:
        return {
            "status": "unknown",
            "reason": "No reference range available"
        }

    param_info = parameter_definitions[parameter_name]
    expected_unit = param_info.get("unit")

    # If gender-aware definitions exist, try to select them
    selected_ranges = None
    if isinstance(param_info.get("by_gender"), dict) and gender:
        g = gender.strip().lower()
        selected_ranges = param_info.get("by_gender", {}).get(g)

    # Age-group selection (optional) - expects dict like {"0-12": {...}}
    if selected_ranges is None and isinstance(param_info.get("by_age_group"), dict) and age is not None:
        for agerange, defs in param_info.get("by_age_group", {}).items():
            try:
                parts = agerange.split("-")
                low = int(parts[0])
                high = int(parts[1]) if len(parts) > 1 else low
            except Exception:
                continue
            if low <= age <= high:
                selected_ranges = defs
                break

    # Fallback to generic 'ranges' if no gender/age-specific found
    if selected_ranges is None:
        selected_ranges = param_info.get("ranges")

    # 2. Missing or invalid value
    if value is None or not isinstance(value, (int, float)):
        return {
            "status": "invalid",
            "reason": "Missing or non-numeric value"
        }

    # 3. Unit mismatch (if unit provided)
    if unit and expected_unit and unit.lower() != expected_unit.lower():
        return {
            "status": "unit_mismatch",
            "expected_unit": expected_unit,
            "received_unit": unit
        }

    # 4. Range evaluation driven by selected_ranges
    ranges = selected_ranges or {}
    if isinstance(ranges, dict):
        for status, bounds in ranges.items():
            # bounds may be a 2-tuple [low, high]
            if isinstance(bounds, (list, tuple)) and len(bounds) == 2:
                low, high = bounds
                if low <= value <= high:
                    return {
                        "status": status,
                        "value": value,
                        "unit": expected_unit
                    }

    # 5. Fallback
    return {
        "status": "unclassified",
        "value": value,
        "unit": expected_unit
    }
