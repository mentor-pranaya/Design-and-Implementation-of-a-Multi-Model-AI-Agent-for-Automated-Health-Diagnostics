"""
Canonical Pattern Registry - Single Source of Truth

All pattern names must match this registry exactly.
No fuzzy matching. No string similarity. Strict equality only.

Usage:
- Pattern detection engine outputs canonical names
- Ground truth uses canonical names
- Evaluation compares canonical names only
"""

# Canonical pattern names - authoritative mapping
PATTERN_REGISTRY = {
    # Hematologic patterns
    "ANEMIA": "Anemia Indicator",
    "ANEMIA_CHRONIC": "Anemia of Chronic Disease",
    
    # Metabolic patterns
    "DIABETES_RISK": "Diabetes Risk",
    "PREDIABETES": "Prediabetes Risk",
    "METABOLIC_SYNDROME": "Metabolic Syndrome",
    
    # Cardiovascular patterns
    "CVD_RISK": "Cardiovascular Risk",
    "HIGH_CHOLESTEROL": "High Cholesterol",
    
    # Organ function patterns
    "KIDNEY_DISEASE": "Kidney Disease",
    "LIVER_ALERT": "Liver Health Alert",
    "THYROID_DYSFUNCTION": "Thyroid Dysfunction",
    
    # Acute conditions
    "ELECTROLYTE_IMBALANCE": "Electrolyte Imbalance"
}

# Reverse mapping for validation
CANONICAL_TO_KEY = {v: k for k, v in PATTERN_REGISTRY.items()}

# All valid pattern names (for validation)
VALID_PATTERN_NAMES = set(PATTERN_REGISTRY.values())


def normalize_pattern_name(pattern_name: str) -> str:
    """
    Normalize a pattern name to canonical form.
    
    Args:
        pattern_name: Raw pattern name from any source
        
    Returns:
        Canonical pattern name or raises ValueError if not recognized
    """
    # Remove extra whitespace
    pattern_name = pattern_name.strip()
    
    # Check if already canonical
    if pattern_name in VALID_PATTERN_NAMES:
        return pattern_name
    
    # Check if it's a registry key
    if pattern_name.upper() in PATTERN_REGISTRY:
        return PATTERN_REGISTRY[pattern_name.upper()]
    
    # Common aliases for backward compatibility
    aliases = {
        "Anemia": "Anemia Indicator",
        "anemia": "Anemia Indicator",
        "Diabetes": "Diabetes Risk",
        "Prediabetes": "Prediabetes Risk",
        "Cardiovascular Risk": "Cardiovascular Risk",
        "CVD Risk": "Cardiovascular Risk",
        "Metabolic Syndrome": "Metabolic Syndrome",
        "High Cholesterol": "High Cholesterol",
        "Kidney Function Assessment": "Kidney Disease",
        "Liver Health Alert": "Liver Health Alert",
        "Electrolyte Imbalance": "Electrolyte Imbalance",
        "Thyroid Dysfunction": "Thyroid Dysfunction",
        "Anemia of Chronic Disease": "Anemia of Chronic Disease"
    }
    
    if pattern_name in aliases:
        return aliases[pattern_name]
    
    raise ValueError(f"Unrecognized pattern name: '{pattern_name}'. Must match PATTERN_REGISTRY.")


def validate_pattern_list(patterns: list) -> list:
    """
    Validate and normalize a list of pattern names.
    
    Args:
        patterns: List of pattern names
        
    Returns:
        List of canonical pattern names
        
    Raises:
        ValueError if any pattern name is invalid
    """
    return [normalize_pattern_name(p) for p in patterns]


if __name__ == "__main__":
    # Self-test
    print("Pattern Registry - Canonical Names")
    print("=" * 60)
    for key, canonical_name in PATTERN_REGISTRY.items():
        print(f"{key:25} → {canonical_name}")
    
    print(f"\nTotal canonical patterns: {len(VALID_PATTERN_NAMES)}")
    
    # Test normalization
    print("\n" + "=" * 60)
    print("Testing Normalization:")
    test_cases = ["Anemia", "anemia", "Diabetes Risk", "ANEMIA"]
    for test in test_cases:
        try:
            canonical = normalize_pattern_name(test)
            print(f"  '{test}' → '{canonical}'")
        except ValueError as e:
            print(f"  '{test}' → ERROR: {e}")
