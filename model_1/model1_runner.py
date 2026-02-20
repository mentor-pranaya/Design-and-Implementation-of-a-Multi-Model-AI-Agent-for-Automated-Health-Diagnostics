from model_1.parameter_evaluator import evaluate_parameter
from model_1.dataset_loader import load_lab_report_ds, load_medical_ner
from model_1.name_normalizer import NameNormalizer
from model_1.explanations import get_explanation
from model_1.unit_mapper import normalize_unit as normalize_unit_str
import os


def run_model_1(structured_data, datasets_base: str = "datasets/lab_report_ds"):
    """Run Model 1 (value normalization and status detection).

    - Loads dataset-driven parameter definitions and medical NER.
    - Normalizes parameter names using the NER mapping.
    - Evaluates each parameter using dataset ranges.
    """
    # Load datasets (parameters and optional patterns)
    ds = load_lab_report_ds(datasets_base)
    parameter_definitions = ds.get("parameters", {})

    # Load NER mapping and normalizer
    ner_base = os.path.join(os.path.dirname(datasets_base), "medical_ner")
    normalizer = NameNormalizer(ner_base_path=ner_base)

    results = {}

    # Flatten nested structured outputs (category -> tests) into param->data
    flat = {}
    for key, val in structured_data.items():
        if isinstance(val, dict):
            # assume nested mapping of tests
            for subk, subv in val.items():
                flat[subk] = subv
        else:
            flat[key] = val

    # Extract patient metadata if present
    age = None
    gender = None
    patient = structured_data.get("patient") or {}
    if isinstance(patient, dict):
        age = patient.get("age") or patient.get("age_years")
        gender = patient.get("gender") or patient.get("sex")
    # allow top-level age/gender
    age = age or structured_data.get("age")
    gender = gender or structured_data.get("gender")

    for raw_param, data in flat.items():
        normalized = normalizer.normalize(raw_param)
        value = data.get("value")
        unit = data.get("unit")

        # Normalize unit strings if present
        if unit:
            try:
                unit = normalize_unit_str(unit)
            except Exception:
                pass

        out = evaluate_parameter(
            parameter_name=normalized,
            value=value,
            unit=unit,
            parameter_definitions=parameter_definitions,
            age=age,
            gender=gender
        )

        # attach explanation text when available
        expl = ""
        try:
            expl = get_explanation(normalized, out.get("status"))
        except Exception:
            expl = ""
        if expl:
            out["explanation"] = expl

        results[normalized] = out

    return results
