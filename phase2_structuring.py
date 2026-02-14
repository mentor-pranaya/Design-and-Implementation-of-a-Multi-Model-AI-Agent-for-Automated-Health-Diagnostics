from structuring_layers.test_dictionary import TEST_ALIASES
from structuring_layers.value_extractor import extract_numeric_value
from structuring_layers.unit_normalizer import normalize_unit
from structuring_layers.bp_extractor import extract_blood_pressure


def structure_report(plain_text: str) -> dict:
    """
    Converts plain medical report text into structured JSON.
    """

    structured_output = {}

    lines = plain_text.split("\n")

    for line in lines:
        line_lower = line.lower()

        # 1️⃣ Special case: Blood Pressure
        if "blood pressure" in line_lower or "bp" in line_lower:
            bp_data = extract_blood_pressure(line)
            if bp_data:
                structured_output.setdefault("vitals", {})["blood_pressure"] = bp_data
            continue

        # 2️⃣ Other medical tests
        for category, tests in TEST_ALIASES.items():
            for test_name, aliases in tests.items():

                if any(alias in line_lower for alias in aliases):

                    value, raw_unit = extract_numeric_value(line)
                    if value is None:
                        continue

                    unit = normalize_unit(test_name, raw_unit)

                    structured_output.setdefault(category, {})[test_name] = {
                        "value": value,
                        "unit": unit,
                        "raw_text": line.strip()
                    }

    return structured_output


# 🔹 TEMPORARY TEST (you can delete this later)
if __name__ == "__main__":
    sample_text = """
    Fasting Blood Sugar : 110 mg/dL
    Total Cholesterol 210 mg/dL
    HDL Cholesterol 38 mg/dL
    Hemoglobin 12.8 g/dL
    Blood Pressure: 120/80 mmHg
    """

    result = structure_report(sample_text)
    print(result)
