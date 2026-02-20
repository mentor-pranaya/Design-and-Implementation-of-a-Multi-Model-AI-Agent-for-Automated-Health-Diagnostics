import json
import argparse
from typing import Dict, Any

from model_2.model2_runner import run_model_2


DOMAIN_DISPLAY = {
    'cardiac': 'Cardiac Risk',
    'diabetes': 'Diabetes Risk',
    'cbc': 'CBC Abnormality',
    'bp': 'Blood Pressure',
    'general': 'General Risk'
}


def _format_pattern(params_list):
    # params_list like ["ldl:high","hdl:low"] -> "LDL high + HDL low"
    parts = []
    for p in params_list:
        try:
            name, status = p.split(":", 1)
        except Exception:
            parts.append(p)
            continue
        pretty_name = name.replace("_", " ").upper()
        parts.append(f"{pretty_name} {status}")
    return " + ".join(parts)


def print_summary(result: Dict[str, Any]):
    model2 = result.get('model_2', {})
    domain_risks = model2.get('domain_risks', {})

    print("--------------------------------------------------")
    if not domain_risks:
        print("No domain risks detected or no patterns matched.")
        print("--------------------------------------------------")
        return

    # prefer common order
    order = ['cardiac', 'diabetes', 'cbc', 'bp', 'general']
    for dom in order:
        info = domain_risks.get(dom)
        if not info:
            continue
        title = DOMAIN_DISPLAY.get(dom, dom.capitalize())
        print(title)
        print(f"Level: {info.get('risk_level', 'unknown').capitalize()}")
        print(f"Severity: {info.get('severity_score', 0.0)}")
        print(f"Confidence: {info.get('confidence', 0.0)}")
        pats = info.get('matched_patterns', [])
        if pats:
            pat_strs = [_format_pattern(p.get('params', [])) for p in pats]
            print(f"Patterns: {', '.join(pat_strs)}")
        else:
            print("Patterns: None")
        reasons = info.get('reasons') or []
        if reasons:
            print(f"Reason: {reasons[0]}")
        print("--------------------------------------------------")


def load_input(path: str) -> Dict[str, Any]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                raise ValueError('Input JSON must be an object mapping parameter->result')
    except Exception as e:
        raise


SAMPLE_INPUT = {
    "ldl": {"value": 160, "status": "high", "unit": "mg/dL"},
    "hdl": {"value": 35, "status": "low", "unit": "mg/dL"},
    "total_cholesterol": {"value": 240, "status": "high", "unit": "mg/dL"},
    "glucose_fasting": {"value": 110, "status": "pre_high", "unit": "mg/dL"},
    "bp_systolic": {"value": 142, "status": "high", "unit": "mmHg"},
    "bp_diastolic": {"value": 92, "status": "high", "unit": "mmHg"},
    "hemoglobin": {"value": 11.2, "status": "low", "unit": "g/dL"},
    "rbc": {"value": 3.8, "status": "low", "unit": "million/uL"}
}


def main():
    parser = argparse.ArgumentParser(description='Run Model 2 on a structured Model 1 JSON output')
    parser.add_argument('--input', '-i', help='Path to JSON file with Model 1 output; if omitted a sample will be used')
    args = parser.parse_args()

    if args.input:
        try:
            data = load_input(args.input)
        except Exception as e:
            print(f"Failed to load input file: {e}")
            return
    else:
        data = SAMPLE_INPUT

    try:
        result = run_model_2(data)
    except Exception as e:
        print(f"Model 2 failed: {e}")
        return

    try:
        print_summary(result)
    except Exception as e:
        print(f"Failed to print summary: {e}")


if __name__ == '__main__':
    main()
