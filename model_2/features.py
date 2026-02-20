"""Feature engineering utilities for Model 2.

Generates derived features from Model 1 output. Handles missing values
and avoids raising on absent parameters.
"""
from typing import Dict, Any, Optional

FEATURE_ORDER = [
    "ldl_hdl_ratio",
    "chol_ratio",
    "glucose_high_flag",
    "anemia_flag",
    "bp_stage_flag",
]


def _get_value(m1_item: Optional[Dict[str, Any]]) -> Optional[float]:
    if not isinstance(m1_item, dict):
        return None
    v = m1_item.get("value")
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def generate_features(model1_output: Dict[str, Any]) -> Dict[str, Any]:
    """Return a dictionary of derived features.

    model1_output: mapping param_name -> model1 result dict (with keys like
    'value' and 'status').

    Features produced (required for ML):
    - ldl_hdl_ratio: numeric or None
    - chol_ratio: numeric or None (total_cholesterol / hdl)
    - glucose_high_flag: bool
    - anemia_flag: bool (hb low OR rbc low)
    - bp_stage_flag: int (0 normal, 1 elevated, 2 stage_1, 3 stage_2, -1 unknown)

    Additional derived fields are included for compatibility.
    """
    out: Dict[str, Any] = {}

    # numeric extraction
    ldl_v = _get_value(model1_output.get("ldl"))
    hdl_v = _get_value(model1_output.get("hdl"))
    tot_v = _get_value(model1_output.get("total_cholesterol"))
    sys_v = _get_value(model1_output.get("bp_systolic"))
    dia_v = _get_value(model1_output.get("bp_diastolic"))
    hb_v = _get_value(model1_output.get("hemoglobin"))
    rbc_v = _get_value(model1_output.get("rbc"))

    # ratios
    out["ldl_hdl_ratio"] = None
    if ldl_v is not None and hdl_v is not None and hdl_v != 0:
        out["ldl_hdl_ratio"] = ldl_v / hdl_v

    out["chol_ratio"] = None
    if tot_v is not None and hdl_v is not None and hdl_v != 0:
        out["chol_ratio"] = tot_v / hdl_v
    out["total_cholesterol_hdl_ratio"] = out["chol_ratio"]

    # BP category logic (use the more severe of systolic/diastolic)
    def _bp_from_values(s, d):
        if s is None and d is None:
            return "unknown"
        # Use standard ACC/AHA categories
        # elevated: systolic 120-129 and diastolic <80
        # stage 1: systolic 130-139 or diastolic 80-89
        # stage 2: systolic >=140 or diastolic >=90
        try:
            if s is not None and s >= 140 or d is not None and d >= 90:
                return "stage_2"
            if s is not None and 130 <= s <= 139 or d is not None and 80 <= d <= 89:
                return "stage_1"
            if s is not None and 120 <= s <= 129 and (d is None or d < 80):
                return "elevated"
            if s is not None and s < 120 and (d is None or d < 80) and (d is None or d < 80):
                return "normal"
            # fallback when only diastolic present
            if s is None and d is not None:
                if d >= 90:
                    return "stage_2"
                if 80 <= d <= 89:
                    return "stage_1"
                if d < 80:
                    return "normal"
        except Exception:
            return "unknown"
        return "unknown"

    bp_category = _bp_from_values(sys_v, dia_v)
    out["bp_category"] = bp_category
    bp_stage_map = {
        "normal": 0,
        "elevated": 1,
        "stage_1": 2,
        "stage_2": 3,
        "unknown": -1,
    }
    out["bp_stage_flag"] = bp_stage_map.get(bp_category, -1)

    # CBC anemia flag: strict AND of hb_low and rbc_low statuses
    hb_status = None
    rbc_status = None
    try:
        if isinstance(model1_output.get("hemoglobin"), dict):
            hb_status = model1_output.get("hemoglobin").get("status")
    except Exception:
        hb_status = None
    try:
        if isinstance(model1_output.get("rbc"), dict):
            rbc_status = model1_output.get("rbc").get("status")
    except Exception:
        rbc_status = None

    out["cbc_anemia_flag"] = bool(hb_status == "low" and rbc_status == "low")
    out["cbc_anemia_possible"] = bool(hb_status == "low" or rbc_status == "low")
    out["anemia_flag"] = out["cbc_anemia_possible"]

    # individual flags
    out["ldl_high"] = isinstance(model1_output.get("ldl"), dict) and model1_output.get("ldl").get("status") == "high"
    out["hdl_low"] = isinstance(model1_output.get("hdl"), dict) and model1_output.get("hdl").get("status") == "low"
    out["hb_low"] = hb_status == "low"
    out["rbc_low"] = rbc_status == "low"
    out["glucose_high_flag"] = isinstance(model1_output.get("glucose_fasting"), dict) and model1_output.get("glucose_fasting").get("status") in ("high", "pre_high")

    # include some raw numeric features for downstream ML/patterns
    out["raw_ldl"] = ldl_v
    out["raw_hdl"] = hdl_v
    out["raw_total_cholesterol"] = tot_v
    out["raw_bp_systolic"] = sys_v
    out["raw_bp_diastolic"] = dia_v
    out["raw_hemoglobin"] = hb_v
    out["raw_rbc"] = rbc_v

    return out


if __name__ == "__main__":
    # small self-check
    sample = {
        "ldl": {"value": 160, "status": "high"},
        "hdl": {"value": 35, "status": "low"},
        "total_cholesterol": {"value": 240, "status": "high"},
        "bp_systolic": {"value": 142, "status": "high"},
        "bp_diastolic": {"value": 92, "status": "high"},
        "hemoglobin": {"value": 11.2, "status": "low"},
        "rbc": {"value": 3.8, "status": "low"},
    }
    print(generate_features(sample))
