import json
import os
from typing import List, Dict, Any


def _default_tag_for_params(params: List[str]) -> List[str]:
    """Heuristic tagging based on parameters present.

    This is simple and conservative; users can override tags later.
    """
    tags = set()
    joined = " ".join(params).lower()
    if any(p.startswith("ldl") or "chol" in p or "hdl" in p for p in params):
        tags.add("cardiac")
    if any("glucose" in p or "hba1c" in p for p in params):
        tags.add("diabetes")
    if any(p.startswith("wbc") or p.startswith("hemoglobin") or p.startswith("rbc") for p in params):
        tags.add("cbc")
    if not tags:
        tags.add("general")
    return list(tags)


def mine_patterns_from_reports(report_dicts: List[Dict]) -> Dict[str, Any]:
    """Mine co-occurrence patterns of abnormal parameter states.

    Input: list of structured reports where each report is either:
      - Model 1 output (param -> {"status": ...}), or
      - raw structured report (param -> {"value":..., "unit":...})

    Output: dict with keys `patterns` (list) and `total_reports`.
    Each pattern has `params` (list of 'param:status'), `count`, `tags`, and `confidence`.
    """
    combo_counts = {}
    reports_processed = 0

    for rep in report_dicts:
        # flatten nested categories
        flat = {}
        if isinstance(rep, dict):
            for k, v in rep.items():
                if isinstance(v, dict) and any(isinstance(x, dict) for x in v.values()):
                    # nested categories
                    for subk, subv in v.items():
                        flat[subk] = subv
                else:
                    flat[k] = v

        # detect statuses (Model 1 output) or skip non-status entries
        observed = set()
        for p, d in flat.items():
            if isinstance(d, dict) and 'status' in d:
                st = d.get('status')
                if st and st not in ('normal', 'invalid', 'unknown', 'unclassified'):
                    observed.add(f"{p}:{st}")

        if observed:
            key = tuple(sorted(observed))
            combo_counts[key] = combo_counts.get(key, 0) + 1

        reports_processed += 1

    patterns = []
    for params_tuple, cnt in sorted(combo_counts.items(), key=lambda x: -x[1]):
        params = list(params_tuple)
        # tags assigned heuristically
        tags = _default_tag_for_params(params)
        patterns.append({
            "params": params,
            "count": cnt,
            "tags": tags,
            # confidence will be computed by dividing by total_reports later
        })

    total = reports_processed or 1
    # compute confidence
    for p in patterns:
        p["confidence"] = float(p.get("count", 0)) / float(total)

    return {"patterns": patterns, "total_reports": reports_processed}


def save_patterns(output_dir: str, patterns_summary: Dict[str, Any]):
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "patterns.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(patterns_summary, f, indent=2)
    return out_file


if __name__ == '__main__':
    # simple CLI: look for structured JSON/JSONL files under candidate dirs
    candidates = ["datasets/lab_report_ds", "lab report ds", "lab_report_ds"]
    reports = []
    for c in candidates:
        if not os.path.exists(c):
            continue
        for dirpath, dirnames, filenames in os.walk(c):
            for fn in filenames:
                if fn.lower().endswith(('.json', '.jsonl', '.ndjson')):
                    try:
                        with open(os.path.join(dirpath, fn), 'r', encoding='utf-8') as fh:
                            data = json.load(fh)
                            if isinstance(data, list):
                                reports.extend(data)
                            elif isinstance(data, dict):
                                reports.append(data)
                    except Exception:
                        continue

    if not reports:
        print("No structured JSON/JSONL reports found in candidates; provide structured Model 1 outputs or run OCR first.")
    else:
        summary = mine_patterns_from_reports(reports)
        out = save_patterns("datasets/lab_report_ds", summary)
        print(f"Wrote patterns to {out}; reports processed: {summary.get('total_reports')}, patterns: {len(summary.get('patterns', []))}")
