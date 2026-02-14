import re

# Matches formats like: 120/80, 130 / 85, BP: 120/80 mmHg
BP_PATTERN = re.compile(r"(\d{2,3})\s*/\s*(\d{2,3})")

def extract_blood_pressure(text: str):
    match = BP_PATTERN.search(text)
    if not match:
        return None

    systolic = int(match.group(1))
    diastolic = int(match.group(2))

    return {
        "systolic": systolic,
        "diastolic": diastolic,
        "unit": "mmHg",
        "raw_text": text.strip()
    }
