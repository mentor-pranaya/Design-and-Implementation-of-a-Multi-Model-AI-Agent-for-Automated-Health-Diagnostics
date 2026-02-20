import json
import os
from typing import Dict, Any, List


def load_lab_report_ds(base_path: str) -> Dict[str, Any]:
    """Load historical lab report patterns for Model 2.

    Expected file: `patterns.json` with structure:
      {
        "patterns": [
          {"params": ["ldl:high","total_cholesterol:high"], "count": 120, "tags": ["cardiac"]},
          ...
        ],
        "total_reports": 10000
      }

    Returns dict with keys `patterns` (list) and `total_reports`.
    """
    result: Dict[str, Any] = {"patterns": [], "total_reports": 0}

    patterns_file = os.path.join(base_path, "patterns.json")
    if not os.path.exists(patterns_file):
        return result

    with open(patterns_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        result["patterns"] = data.get("patterns", [])
        result["total_reports"] = data.get("total_reports", 0)

    # Normalize pattern params into sets for faster matching
    for p in result["patterns"]:
        params = p.get("params", [])
        p["_param_set"] = set(params)
        # ensure tags is a list
        p["tags"] = p.get("tags", []) or []

    return result
