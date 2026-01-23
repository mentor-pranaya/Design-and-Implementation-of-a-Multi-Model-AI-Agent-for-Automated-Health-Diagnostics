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
 
    text_lower = text.lower()
    
    # Pattern 1: "age/gender : 54 y 6 m 27 d/f" or "age/gender : 24 y 0 m 0 d /m"
    pattern1 = r'age\s*/\s*gender\s*:?\s*(\d+)\s*y'
    match = re.search(pattern1, text_lower)
    if match:
        age = int(match.group(1))
        if 1 <= age <= 120:
            return age
    
    # Pattern 2: "age / gender : 39 year(s) / male"
    pattern2 = r'age\s*/\s*gender\s*:?\s*(\d+)\s*year'
    match = re.search(pattern2, text_lower)
    if match:
        age = int(match.group(1))
        if 1 <= age <= 120:
            return age
    
    # Pattern 3: "sex/age male / 41 y" or "sex/age : male / 41 y"
    pattern3 = r'sex\s*/\s*age\s*:?\s*(?:male|female|m|f)\s*/?\s*(\d+)\s*y?'
    match = re.search(pattern3, text_lower)
    if match:
        age = int(match.group(1))
        if 1 <= age <= 120:
            return age
    
    # Pattern 4: "age/sex 25/f" or "age/sex: 30/m"
    pattern4 = r'age\s*/\s*sex\s*:?\s*(\d+)\s*/?\s*(?:male|female|m|f)'
    match = re.search(pattern4, text_lower)
    if match:
        age = int(match.group(1))
        if 1 <= age <= 120:
            return age
    
    # Pattern 5: "age 25y" or "age 25y 10m 26d" or "age: 25y"
    # Also handles OCR errors like "aae", "aqe"
    pattern5 = r'(?:age|aae|aqe)\s*:?\s*(\d+)\s*y(?:ears?|rs|r)?'
    match = re.search(pattern5, text_lower)
    if match:
        age = int(match.group(1))
        if 1 <= age <= 120:
            return age
    
    # Pattern 6: "age: 25 years" or "age 25 years" or "aae: 21 year"
    pattern6 = r'(?:age|aae|aqe)\s*:?\s*(\d+)\s+(?:years?|yrs|yr)'
    match = re.search(pattern6, text_lower)
    if match:
        age = int(match.group(1))
        if 1 <= age <= 120:
            return age
    
    # Pattern 7: "age: 25" or "age 25" (standalone)
    pattern7 = r'(?:age|aae|aqe)\s*:?\s*(\d+)(?!\s*/)'
    match = re.search(pattern7, text_lower)
    if match:
        age = int(match.group(1))
        if 1 <= age <= 120:
            return age
    
    return None

def extract_gender(text):
  
    text_lower = text.lower()
    
    # Pattern 1: "age/gender : 54 y 6 m 27 d/f" or "age/gender : 24 y 0 m 0 d /m"
    # Gender is at the end after "d/"
    pattern1 = r'age\s*/\s*gender\s*:?\s*\d+\s*y.*?d\s*/?\s*([mf])\b'
    match = re.search(pattern1, text_lower)
    if match:
        gender_char = match.group(1)
        return "male" if gender_char == "m" else "female"
    
    # Pattern 2: "age/gender : 54 y ... /female" or "age/gender : 39 year(s) / male"
    pattern2 = r'age\s*/\s*gender\s*:?\s*\d+.*?/\s*(male|female)\b'
    match = re.search(pattern2, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 3: "sex/age male / 41" or "sex/age : male / 41"
    pattern3 = r'sex\s*/\s*age\s*:?\s*(male|female)\s*/?\s*\d+'
    match = re.search(pattern3, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 4: "sex/age m / 41" (short form)
    pattern4 = r'sex\s*/\s*age\s*:?\s*([mf])\s*/?\s*\d+'
    match = re.search(pattern4, text_lower)
    if match:
        gender_char = match.group(1)
        return "male" if gender_char == "m" else "female"
    
    # Pattern 5: "age/sex 25/female" or "age/sex: 30/male"
    pattern5 = r'age\s*/\s*sex\s*:?\s*\d+\s*/?\s*(male|female)'
    match = re.search(pattern5, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 6: "age/sex 25/f" (short form)
    pattern6 = r'age\s*/\s*sex\s*:?\s*\d+\s*/?\s*([mf])\b'
    match = re.search(pattern6, text_lower)
    if match:
        gender_char = match.group(1)
        return "male" if gender_char == "m" else "female"
    
    # Pattern 7: "sex female" or "sex: female" or "sex : male"
    pattern7 = r'\bsex\s*:\s*(male|female)\b'
    match = re.search(pattern7, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 8: "gender female" or "gender: male"
    pattern8 = r'gender\s*:?\s*(male|female)'
    match = re.search(pattern8, text_lower)
    if match:
        return match.group(1)
    
    # Pattern 9: "sex m" or "sex: f" (short form)
    pattern9 = r'\bsex\s*:?\s*([mf])\b'
    match = re.search(pattern9, text_lower)
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