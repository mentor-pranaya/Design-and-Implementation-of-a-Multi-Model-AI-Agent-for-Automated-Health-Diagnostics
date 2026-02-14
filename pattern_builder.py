import os
import json
from typing import List, Dict


def find_structured_reports(root: str) -> List[str]:
    matches = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(('.json', '.jsonl', '.ndjson')):
                matches.append(os.path.join(dirpath, fn))
    return matches


def load_json_reports(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # If file contains a list, return list; if single dict, return [dict]
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            return []


def build_patterns_from_reports(report_dicts: List[Dict]) -> Dict:
    """Given a list of structured reports (not raw images), build co-occurrence patterns.

    Each report_dict is expected to be similar to the `structured_data` passed to Model 1:
      {category: {param: {"value": ..., "unit": ...}, ...}, ...}

    This function DOES NOT perform OCR. It aggregates abnormal parameter co-occurrences
    using Model 1's evaluator by calling the runner when available.
    """
    try:
        from model_1.model1_runner import run_model_1
    except Exception:
        run_model_1 = None

    combo_counts = {}
    reports_processed = 0

    for rep in report_dicts:
        # rep should already be a structured mapping; pass to Model 1 if available
        if run_model_1:
            try:
                m1_out = run_model_1(rep)
            except Exception:
                m1_out = {}
        else:
            m1_out = {}

        # fall back: if rep already contains statuses (model1 output), use it
        if not m1_out and isinstance(rep, dict):
            # flatten if nested categories present
            flat = {}
            for k, v in rep.items():
                if isinstance(v, dict):
                    for subk, subv in v.items():
                        flat[subk] = subv
                else:
                    flat[k] = v

            # detect if statuses present
            for p, d in flat.items():
                if isinstance(d, dict) and 'status' in d:
                    m1_out[p] = d

        # collect abnormal tags like 'ldl:high'
        observed = set()
        for p, info in (m1_out or {}).items():
            if not isinstance(info, dict):
                continue
            st = info.get('status')
            if st and st not in ('normal', 'invalid', 'unknown', 'unclassified'):
                observed.add(f"{p}:{st}")

        if observed:
            key = tuple(sorted(observed))
            combo_counts[key] = combo_counts.get(key, 0) + 1

        reports_processed += 1

    # convert combo_counts to patterns list
    patterns = []
    for params_tuple, cnt in sorted(combo_counts.items(), key=lambda x: -x[1]):
        patterns.append({
            "params": list(params_tuple),
            "count": cnt,
            "tags": []
        })

    return {"patterns": patterns, "total_reports": reports_processed}


def main(source_dirs: List[str], output_dir: str = 'datasets/lab_report_ds'):
    # find structured files in any of the provided source directories
    reports = []
    for sd in source_dirs:
        if not os.path.exists(sd):
            continue
        files = find_structured_reports(sd)
        for f in files:
            try:
                reports.extend(load_json_reports(f))
            except Exception:
                # ignore malformed files
                continue

    if not reports:
        print('No structured JSON/JSONL reports found in:', source_dirs)
        print('Pattern building requires structured reports. Provide JSON/JSONL files or run OCR separately.')
        return

    summary = build_patterns_from_reports(reports)

    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, 'patterns.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f'Wrote patterns.json to {out_file} — reports processed: {summary.get("total_reports")}, patterns: {len(summary.get("patterns",[]))}')


if __name__ == '__main__':
    # default source directories to check (existing extracted folders)
    candidates = ['datasets/lab_report_ds', 'lab report ds', 'lab_report_ds']
    main(candidates)
