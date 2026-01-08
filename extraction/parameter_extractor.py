import re

def extract_parameters(text):
    text = text.lower()
    results = {}

    # remove extra spaces
    text = re.sub(r"\s+", " ", text)

    patterns = {
        "hemoglobin": r"(hb|h[a-z]*moglobin)[^\d]{0,10}(\d+\.?\d*)",
        "wbc_count": r"(wbc|white|total|leucocyte)[^\d]{0,20}(\d{3,5})",

        "platelet_count": r"(platelet|plt)[^\d]{0,15}(\d{3,6})",
        "rbc_count": r"(rbc)[^\d]{0,10}(\d+\.?\d*)",
        "mcv": r"(mcv)[^\d]{0,10}(\d+\.?\d*)",
        "mchc": r"(mchc)[^\d]{0,10}(\d+\.?\d*)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            results[key] = float(match.group(2))

    return results
