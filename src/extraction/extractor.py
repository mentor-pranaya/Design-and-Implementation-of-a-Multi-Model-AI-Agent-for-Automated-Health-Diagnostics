import re


# Expected medical ranges

EXPECTED_RANGES = {

    # ---- CBC ----
    "hemoglobin": (8.0, 18.0),
    "rbc": (2.5, 6.5),
    "wbc": (3.0, 12.0),
    "platelet": (100.0, 500.0),
    "plt": (100.0, 500.0),
    "hct": (30.0, 55.0),
    "mcv": (75.0, 105.0),
    "mch": (24.0, 35.0),
    "mchc": (30.0, 37.0),
    "rdw-cv": (10.0, 16.0),
    "rdw-sd": (35.0, 60.0),

    # ---- KFT ----
    "creatinine": (0.4, 1.5),
    "urea": (10.0, 50.0),
    "uric acid": (2.5, 7.5)
}


# Alias expansion (KEY FIX)

PARAM_ALIASES = {
    "platelet": ["platelet", "platelet count", "platelets", "plt"],
    "plt": ["platelet", "platelet count", "platelets", "plt"],
    "creatinine": ["creatinine", "serum creatinine"],
    "urea": ["urea", "blood urea"],
    "uric acid": ["uric acid"]
}

# Primary stop words only
STOP_PARAMS = [
    "hemoglobin", "rbc", "wbc", "platelet",
    "hct", "mcv", "mch", "mchc",
    "rdw-cv", "rdw-sd",
    "creatinine", "urea", "uric acid"
]


# Default units

DEFAULT_UNITS = {
    "hemoglobin": "g/dl",
    "rbc": "10^6/uL",
    "wbc": "10^3/uL",
    "platelet": "10^3/uL",
    "plt": "10^3/uL",
    "hct": "%",
    "mcv": "fl",
    "mch": "pg",
    "mchc": "g/dl",
    "rdw-cv": "%",
    "rdw-sd": "fl",
    "creatinine": "mg/dl",
    "urea": "mg/dl",
    "uric acid": "mg/dl"
}



# Helpers

def extract_numbers_from_text(text):
    numbers = []
    for match in re.finditer(r"\d+\.?\d*", text):
        try:
            num = float(match.group())
            if 0.01 <= num <= 10000:
                numbers.append(num)
        except ValueError:
            pass
    return numbers


def find_local_context(text, keyword, max_chars=150):
    text = text.lower()
    start = text.find(keyword)
    if start == -1:
        return ""

    start += len(keyword)
    substring = text[start:start + max_chars]

    earliest_stop = len(substring)
    for stop in STOP_PARAMS:
        if stop == keyword:
            continue
        pos = substring.find(stop)
        if 0 <= pos < earliest_stop:
            earliest_stop = pos

    return substring[:earliest_stop].strip()



# Main extractor

def extract_parameter(text, param_name, keywords):
    param_key = param_name.lower()

    #  Expand aliases automatically
    search_terms = set(keywords)
    search_terms.update(PARAM_ALIASES.get(param_key, []))

    for keyword in search_terms:
        context = find_local_context(text, keyword)
        if not context:
            continue

        numbers = extract_numbers_from_text(context)
        if not numbers:
            continue

        expected_min, expected_max = EXPECTED_RANGES.get(
            param_key, (0, float("inf"))
        )

        value = None
        idx = -1
        for i, num in enumerate(numbers):
            if expected_min <= num <= expected_max:
                value = num
                idx = i
                break

        if value is None:
            continue

        # Platelet OCR digit-drop fix
        if param_key in ["platelet", "plt"] and value < 20:
            value *= 10

        # Reference range
        reference_range = None
        tail = numbers[idx + 1:]
        if len(tail) >= 2 and tail[0] < tail[1]:
            reference_range = f"{tail[0]}-{tail[1]}"

        if param_key in ["platelet", "plt"]:
            reference_range = "150.0-450.0"

        unit = DEFAULT_UNITS.get(param_key)

        return {
            param_name: {
                "value": value,
                "unit": unit,
                "reference_range": reference_range
            }
        }

    return {}
