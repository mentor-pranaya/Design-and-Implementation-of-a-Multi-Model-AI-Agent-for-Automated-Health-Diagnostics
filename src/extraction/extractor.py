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



# Age and Gender Extraction Functions


def extract_age(text):
    """
    Extract age from text
    Handles formats like:
        - "age 25y 10m 26d"
        - "Age: 25 years"
        - "Age/Gender: 20/Male"
        - "Age/Gender : 54 Y 6 M 27 D/F"
        - "age 54 y"
        - "20/Male" (age/gender combined)
    
    Returns:
        int: Age in years, or None if not found
    """
    text_lower = text.lower()
    
    # Pattern 1: "age/gender: 20/male" or "age/gender : 20/male"
    pattern1 = r'age\s*/\s*gender\s*:?\s*(\d+)\s*/\s*(?:male|female|m|f)'
    match = re.search(pattern1, text_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 2: "age/gender : 54 y 6 m 27 d/f"
    pattern2 = r'age\s*/\s*gender\s*:?\s*(\d+)\s*y'
    match = re.search(pattern2, text_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 3: "age 25y 10m 26d" or "age 25 y"
    pattern3 = r'age\s*:?\s*(\d+)\s*y'
    match = re.search(pattern3, text_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 4: "age: 25 years" or "age : 25 year"
    pattern4 = r'age\s*:?\s*(\d+)\s*year'
    match = re.search(pattern4, text_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 5: "age: 25" or "age 25"
    pattern5 = r'age\s*:?\s*(\d+)'
    match = re.search(pattern5, text_lower)
    if match:
        age = int(match.group(1))
        if 0 < age < 120:  # Reasonable age range
            return age
    
    # Pattern 6: Standalone "20/male" or "25/female" pattern near age context
    pattern6 = r'(\d{1,3})\s*/\s*(?:male|female)'
    match = re.search(pattern6, text_lower)
    if match:
        age = int(match.group(1))
        if 0 < age < 120:
            return age
    
    return None

def extract_gender(text):
    """
    Extract gender from text
    Handles formats like:
        - "sex female" or "sex: male"
        - "Age/Gender: 20/Male"
        - "age/gender : 54 y 6 m 27 d/f"
        - "20/Male" pattern
    """
    text_lower = text.lower()
    
    # Pattern 1: "age/gender: 20/male" or "age/gender : 20/female"
    pattern1 = r'age\s*/\s*gender\s*:?\s*\d+\s*/\s*(male|female)'
    match = re.search(pattern1, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 2: "age/gender: 20/m" or "age/gender : 20/f"
    pattern2 = r'age\s*/\s*gender\s*:?\s*\d+\s*/\s*([mf])\b'
    match = re.search(pattern2, text_lower)
    if match:
        gender_char = match.group(1)
        return "male" if gender_char == "m" else "female"
    
    # Pattern 3: "age/gender : 54 y 6 m 27 d/f" or "age/gender : 24 y 0 m 0 d /m"
    pattern3 = r'age\s*/\s*gender\s*:?\s*\d+\s*y.*?/\s*([mf])\b'
    match = re.search(pattern3, text_lower)
    if match:
        gender_char = match.group(1)
        return "male" if gender_char == "m" else "female"
    
    # Pattern 4: "age/gender : 54 y ... /female" or "age/gender : 39 year(s) / male"
    pattern4 = r'age\s*/\s*gender\s*:?\s*\d+.*?/\s*(male|female)\b'
    match = re.search(pattern4, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 5: "sex female" or "sex male" (NO colon)
    pattern5 = r'\bsex\s+(male|female)\b'
    match = re.search(pattern5, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 6: "sex: female" or "sex : male" (WITH colon)
    pattern6 = r'\bsex\s*:\s*(male|female)\b'
    match = re.search(pattern6, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 7: "gender female" or "gender: male"
    pattern7 = r'gender\s*:?\s*(male|female)'
    match = re.search(pattern7, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 8: "sex m" or "sex f" or "sex: m"
    pattern8 = r'\bsex\s*:?\s*([mf])\b'
    match = re.search(pattern8, text_lower)
    if match:
        gender_char = match.group(1)
        return "male" if gender_char == "m" else "female"
    
    # Pattern 9: Standalone number/gender like "20/male"
    pattern9 = r'\b\d{1,3}\s*/\s*(male|female)\b'
    match = re.search(pattern9, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 10: Standalone number/m or number/f like "20/m"
    pattern10 = r'\b\d{1,3}\s*/\s*([mf])\b'
    match = re.search(pattern10, text_lower)
    if match:
        gender_char = match.group(1)
        return "male" if gender_char == "m" else "female"
    
    return None



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


def normalize_ocr_range(low_str, high_str):
    if "." not in low_str and "." in high_str:
        try:
            low_val = float(low_str)
            high_val = float(high_str)
        except ValueError:
            return low_str, high_str

        if low_val > high_val and len(low_str) == 2:
            low_str = f"{low_str[0]}.{low_str[1]}"

    return low_str, high_str


def normalize_count_value(param_key, value):
    if value is None:
        return value

    if param_key == "wbc" and value >= 1000:
        return value / 1000.0
    if param_key in ["platelet", "plt"] and value >= 10000:
        return value / 1000.0

    return value


def normalize_count_range(param_key, low, high):
    if low is None or high is None:
        return low, high

    if param_key == "wbc" and low >= 1000 and high >= 1000:
        return low / 1000.0, high / 1000.0
    if param_key in ["platelet", "plt"] and low >= 10000 and high >= 10000:
        return low / 1000.0, high / 1000.0

    return low, high


def parse_value_range_from_context(context, param_key=None):
    value_match = re.search(r"(-?\d+(?:\.\d+)?)", context)
    if not value_match:
        return None

    value_str = value_match.group(1)
    try:
        value = float(value_str)
    except ValueError:
        return None

    if param_key:
        value = normalize_count_value(param_key, value)

    remainder = context[value_match.end():]

    range_match = re.search(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", remainder)
    if not range_match:
        return {
            "value": value,
            "range": None
        }

    low_str, high_str = normalize_ocr_range(range_match.group(1), range_match.group(2))
    try:
        low_val = float(low_str)
        high_val = float(high_str)
    except ValueError:
        return {
            "value": value,
            "range": None
        }

    if param_key:
        low_val, high_val = normalize_count_range(param_key, low_val, high_val)

    return {
        "value": value,
        "range": f"{low_val}-{high_val}"
    }


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
    
    # Special handling for Age
    if param_key == "age":
        age = extract_age(text)
        if age:
            return {
                param_name: {
                    "value": age,
                    "unit": "years",
                    "reference_range": "N/A"
                }
            }
        return {}
    
    # Special handling for Gender
    if param_key == "gender":
        gender = extract_gender(text)
        if gender:
            return {
                param_name: {
                    "value": gender,
                    "unit": "",
                    "reference_range": "N/A"
                }
            }
        return {}
    
    
    search_terms = set(keywords)
    search_terms.update(PARAM_ALIASES.get(param_key, []))

    for keyword in search_terms:
        context = find_local_context(text, keyword)
        if not context:
            continue

        expected_min, expected_max = EXPECTED_RANGES.get(
            param_key, (0, float("inf"))
        )

        parsed = parse_value_range_from_context(context, param_key)
        if parsed:
            value = parsed["value"]

            if value is not None and (parsed["range"] or expected_min <= value <= expected_max):
                unit = DEFAULT_UNITS.get(param_key)
                return {
                    param_name: {
                        "value": value,
                        "unit": unit,
                        "reference_range": parsed["range"]
                    }
                }

        numbers = extract_numbers_from_text(context)
        if not numbers:
            continue

        value = None
        idx = -1
        for i, num in enumerate(numbers):
            if expected_min <= num <= expected_max:
                value = num
                idx = i
                break

        if value is None:
            continue

       
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