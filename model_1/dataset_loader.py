import json
import os
from typing import Dict, Any


def load_lab_report_ds(base_path: str) -> Dict[str, Any]:
    """Load lab_report_ds parameter definitions and pattern stats.

    Expects files under `base_path` such as `parameters.json` and optionally
    `patterns.json`. Returns a dict with keys `parameters`, `patterns`,
    and `total_reports` when available.
    """
    result = {"parameters": {}, "patterns": [], "total_reports": 0}

    params_file = os.path.join(base_path, "parameters.json")
    if os.path.exists(params_file):
        with open(params_file, "r", encoding="utf-8") as f:
            result["parameters"] = json.load(f)

    patterns_file = os.path.join(base_path, "patterns.json")
    if os.path.exists(patterns_file):
        with open(patterns_file, "r", encoding="utf-8") as f:
            pdata = json.load(f)
            # patterns: list of {params: [...], count: int}
            result["patterns"] = pdata.get("patterns", [])
            result["total_reports"] = pdata.get("total_reports", 0)

    return result


def load_medical_ner(base_path: str) -> Dict[str, str]:
    """Load medical NER synonyms mapping.

    Expected format: `synonyms.json` mapping canonical_name -> [alias, ...]
    This returns alias->canonical mapping for quick lookup.
    """
    file_path = os.path.join(base_path, "synonyms.json")
    mapping = {}
    if not os.path.exists(file_path):
        return mapping

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for canonical, aliases in data.items():
            mapping[canonical.lower()] = canonical
            for a in aliases:
                mapping[a.lower()] = canonical

    return mapping
