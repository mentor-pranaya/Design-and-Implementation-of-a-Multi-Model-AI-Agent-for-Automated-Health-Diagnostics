"""
Gold Standard Test Dataset Structure

This module defines the format for annotated ground truth data used for
validating the multi-model AI diagnostic system.

Dataset Components:
1. Extraction Ground Truth: Expected parameter values from reports
2. Classification Ground Truth: Expected clinical status (Low/Normal/High)
3. Pattern Ground Truth: Expected patterns to be detected
4. Risk Score Ground Truth: Expected risk categories

This enables calculation of:
- Extraction accuracy (%)
- Classification accuracy, precision, recall, F1
- Pattern detection sensitivity/specificity
- Risk scoring directional correctness
"""

from typing import Dict, Any, List
from enum import Enum


class ClassificationLabel(Enum):
    """Ground truth classification labels."""
    CRITICAL_LOW = "critical_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL_HIGH = "critical_high"


class PatternLabel(Enum):
    """Ground truth pattern labels."""
    ANEMIA = "anemia_indicator"
    DIABETES_RISK = "diabetes_risk"
    HIGH_CHOLESTEROL = "high_cholesterol"
    KIDNEY_FUNCTION = "kidney_function_alert"
    LIVER_FUNCTION = "liver_function_alert"
    THYROID_DISORDER = "thyroid_disorder"


class RiskCategory(Enum):
    """Ground truth risk categories."""
    LOW = "Low"
    BORDERLINE = "Borderline"
    INTERMEDIATE = "Intermediate"
    HIGH = "High"


# ===========================================================================
# GOLD STANDARD DATA STRUCTURE
# ===========================================================================

GOLD_STANDARD_DATASET = {
    "test_case_1": {
        "patient_id": "TC001",
        "description": "High-risk male patient with diabetes, hypertension, smoking",
        "source_file": "sample_blood_report_1.json",
        
        # ====== EXTRACTION GROUND TRUTH ======
        "extraction_ground_truth": {
            "parameters": [
                {"name": "Hemoglobin", "value": 14.5, "unit": "g/dL"},
                {"name": "RBC", "value": 5.2, "unit": "million cells/μL"},
                {"name": "WBC", "value": 7500, "unit": "cells/μL"},
                {"name": "Platelets", "value": 250000, "unit": "cells/μL"},
                {"name": "Glucose", "value": 135, "unit": "mg/dL"},
                {"name": "Creatinine", "value": 1.1, "unit": "mg/dL"},
                {"name": "Total Cholesterol", "value": 220, "unit": "mg/dL"},
                {"name": "HDL", "value": 45, "unit": "mg/dL"},
                {"name": "LDL", "value": 145, "unit": "mg/dL"},
                {"name": "Triglycerides", "value": 180, "unit": "mg/dL"},
                {"name": "ALT", "value": 32, "unit": "U/L"},
                {"name": "AST", "value": 28, "unit": "U/L"}
            ],
            "total_expected": 12
        },
        
        # ====== CLASSIFICATION GROUND TRUTH ======
        "classification_ground_truth": {
            "Hemoglobin": {"status": "normal", "severity": None},
            "RBC": {"status": "normal", "severity": None},
            "WBC": {"status": "normal", "severity": None},
            "Platelets": {"status": "normal", "severity": None},
            "Glucose": {"status": "high", "severity": "severe", "rationale": "135 mg/dL >> 100 (fasting threshold)"},
            "Creatinine": {"status": "normal", "severity": None},
            "Total Cholesterol": {"status": "high", "severity": "mild", "rationale": "220 mg/dL > 200"},
            "HDL": {"status": "normal", "severity": None, "rationale": "45 mg/dL > 40 (male threshold)"},
            "LDL": {"status": "high", "severity": "severe", "rationale": "145 mg/dL >> 100 optimal"},
            "Triglycerides": {"status": "high", "severity": "moderate", "rationale": "180 mg/dL > 150"},
            "ALT": {"status": "normal", "severity": None},
            "AST": {"status": "normal", "severity": None}
        },
        
        # ====== PATTERN GROUND TRUTH ======
        "pattern_ground_truth": {
            "expected_patterns": [
                {
                    "pattern": "Diabetes Risk",
                    "confidence": "high",
                    "triggered_by": ["Glucose"],
                    "rationale": "Elevated fasting glucose + known diabetic"
                },
                {
                    "pattern": "High Cholesterol",
                    "confidence": "high",
                    "triggered_by": ["LDL", "Triglycerides", "Total Cholesterol"],
                    "rationale": "Multiple lipid abnormalities"
                }
            ],
            "absent_patterns": ["Anemia Indicator", "Kidney Function Alert", "Liver Function Alert"]
        },
        
        # ====== RISK SCORING GROUND TRUTH ======
        "risk_scoring_ground_truth": {
            "cardiovascular": {
                "expected_category": "High",
                "expected_range": {"min": 20, "max": 30},  # 10-year risk %
                "rationale": "Age 45, male, diabetes, HTN, smoking, elevated LDL",
                "expected_triggers": [
                    "Age (40-49)",
                    "Male sex",
                    "Elevated LDL",
                    "Smoker",
                    "Hypertension",
                    "Diabetes"
                ]
            }
        },
        
        # ====== METADATA ======
        "metadata": {
            "annotator": "Clinical expert",
            "annotation_date": "2026-02-12",
            "confidence": "high",
            "notes": "Clear high-risk case with multiple cardiovascular risk factors"
        }
    },
    
    "test_case_2": {
        "patient_id": "TC002",
        "description": "Young female with mild anemia, vegetarian diet",
        "source_file": "sample_blood_report_2.json",
        
        # ====== EXTRACTION GROUND TRUTH ======
        "extraction_ground_truth": {
            "parameters": [
                {"name": "Hemoglobin", "value": 11.5, "unit": "g/dL"},
                {"name": "RBC", "value": 4.0, "unit": "million cells/μL"},
                {"name": "WBC", "value": 6200, "unit": "cells/μL"},
                {"name": "Platelets", "value": 220000, "unit": "cells/μL"},
                {"name": "Glucose", "value": 88, "unit": "mg/dL"},
                {"name": "Total Cholesterol", "value": 185, "unit": "mg/dL"},
                {"name": "HDL", "value": 62, "unit": "mg/dL"},
                {"name": "LDL", "value": 98, "unit": "mg/dL"},
                {"name": "Triglycerides", "value": 125, "unit": "mg/dL"},
                {"name": "TSH", "value": 3.2, "unit": "mIU/L"}
            ],
            "total_expected": 10
        },
        
        # ====== CLASSIFICATION GROUND TRUTH ======
        "classification_ground_truth": {
            "Hemoglobin": {"status": "low", "severity": "mild", "rationale": "11.5 g/dL < 12.0 (female threshold)"},
            "RBC": {"status": "low", "severity": "mild", "rationale": "4.0 < 4.2 (female range)"},
            "WBC": {"status": "normal", "severity": None},
            "Platelets": {"status": "normal", "severity": None},
            "Glucose": {"status": "normal", "severity": None},
            "Total Cholesterol": {"status": "normal", "severity": None},
            "HDL": {"status": "normal", "severity": None},
            "LDL": {"status": "normal", "severity": None},
            "Triglycerides": {"status": "normal", "severity": None},
            "TSH": {"status": "normal", "severity": None}
        },
        
        # ====== PATTERN GROUND TRUTH ======
        "pattern_ground_truth": {
            "expected_patterns": [
                {
                    "pattern": "Anemia Indicator",
                    "confidence": "moderate",
                    "triggered_by": ["Hemoglobin", "RBC"],
                    "rationale": "Low hemoglobin and RBC, likely iron deficiency (vegetarian diet)"
                }
            ],
            "absent_patterns": ["Diabetes Risk", "High Cholesterol", "Kidney Function Alert"]
        },
        
        # ====== RISK SCORING GROUND TRUTH ======
        "risk_scoring_ground_truth": {
            "cardiovascular": {
                "expected_category": "Low",
                "expected_range": {"min": 2, "max": 5},
                "rationale": "Young age (32), female, no risk factors, healthy lipid profile",
                "expected_triggers": ["Age (<40)"]
            }
        },
        
        # ====== METADATA ======
        "metadata": {
            "annotator": "Clinical expert",
            "annotation_date": "2026-02-12",
            "confidence": "high",
            "notes": "Classic presentation of mild iron deficiency anemia in young vegetarian female"
        }
    },
    
    # ====================================================================
    # TEST CASE 3: Borderline Values - Metabolic Syndrome
    # ====================================================================
    "test_case_3": {
        "description": "Borderline values - metabolic syndrome with subclinical markers",
        "source_file": "sample_blood_report_3.json",
        "patient_context": {
            "age": 58,
            "sex": "male",
            "known_conditions": ["prediabetes", "obesity"],
            "lifestyle": {
                "smoker": False,
                "exercise_level": "sedentary",
                "diet_type": "high_carb",
                "alcohol_use": "moderate"
            }
        },
        "extraction_ground_truth": {
            "parameters": {
                "Glucose": {"expected_value": 105, "unit": "mg/dL"},
                "HbA1c": {"expected_value": 6.2, "unit": "%"},
                "Total Cholesterol": {"expected_value": 205, "unit": "mg/dL"},
                "LDL": {"expected_value": 135, "unit": "mg/dL"},
                "HDL": {"expected_value": 38, "unit": "mg/dL"},
                "Triglycerides": {"expected_value": 175, "unit": "mg/dL"},
                "ALT": {"expected_value": 48, "unit": "U/L"},
                "AST": {"expected_value": 42, "unit": "U/L"},
                "Total Bilirubin": {"expected_value": 0.9, "unit": "mg/dL"}
            }
        },
        "classification_ground_truth": {
            "Glucose": {
                "status": "High",
                "severity": "Mild",
                "rationale": "105 mg/dL is borderline (100-125 = prediabetes range)"
            },
            "HbA1c": {
                "status": "High",
                "severity": "Mild",
                "rationale": "6.2% indicates prediabetes (5.7-6.4%)"
            },
            "Total Cholesterol": {
                "status": "High",
                "severity": "Mild",
                "rationale": "205 mg/dL just above optimal (<200)"
            },
            "LDL": {
                "status": "High",
                "severity": "Moderate",
                "rationale": "135 mg/dL near-optimal to borderline high"
            },
            "HDL": {
                "status": "Low",
                "severity": "Moderate",
                "rationale": "38 mg/dL below 40 increases CV risk"
            },
            "Triglycerides": {
                "status": "High",
                "severity": "Mild",
                "rationale": "175 mg/dL borderline high (150-199)"
            },
            "ALT": {
                "status": "High",
                "severity": "Mild",
                "rationale": "48 U/L slightly above normal, suggests fatty liver"
            },
            "AST": {
                "status": "Normal",
                "severity": None,
                "rationale": "42 U/L within normal range"
            },
            "Total Bilirubin": {
                "status": "Normal",
                "severity": None,
                "rationale": "0.9 mg/dL within normal range"
            }
        },
        "pattern_ground_truth": {
            "expected_patterns": [
                {
                    "pattern": "Metabolic Syndrome",
                    "confidence": "high",
                    "supporting_evidence": ["high triglycerides", "low HDL", "elevated glucose", "obesity"]
                },
                {
                    "pattern": "Prediabetes Risk",
                    "confidence": "high",
                    "supporting_evidence": ["glucose 105", "HbA1c 6.2%"]
                },
                {
                    "pattern": "Liver Health Alert",
                    "confidence": "moderate",
                    "supporting_evidence": ["elevated ALT", "metabolic syndrome"]
                }
            ],
            "absent_patterns": ["Acute Kidney Injury", "Anemia"]
        },
        "risk_scoring_ground_truth": {
            "cardiovascular": {
                "expected_category": "Intermediate",
                "expected_range": {"min": 10, "max": 18},
                "expected_triggers": ["Age >55", "Low HDL", "Elevated LDL", "Prediabetes"],
                "rationale": "Age 58, metabolic syndrome markers, borderline lipids"
            }
        },
        "metadata": {
            "annotator": "Clinical expert",
            "annotation_date": "2026-02-13",
            "confidence": "high",
            "notes": "Challenging borderline case - tests threshold detection sensitivity"
        }
    },
    
    # ====================================================================
    # TEST CASE 4: Critical Values - Severe Kidney Dysfunction
    # ====================================================================
    "test_case_4": {
        "description": "Critical values - severe kidney dysfunction with electrolyte imbalance",
        "source_file": "sample_blood_report_4.json",
        "patient_context": {
            "age": 72,
            "sex": "female",
            "known_conditions": ["chronic_kidney_disease", "hypertension", "diabetes"],
            "lifestyle": {
                "smoker": False,
                "exercise_level": "limited",
                "diet_type": "low_sodium",
                "alcohol_use": "none"
            }
        },
        "extraction_ground_truth": {
            "parameters": {
                "Creatinine": {"expected_value": 3.8, "unit": "mg/dL"},
                "BUN": {"expected_value": 68, "unit": "mg/dL"},
                "Potassium": {"expected_value": 5.9, "unit": "mEq/L"},
                "Sodium": {"expected_value": 132, "unit": "mEq/L"},
                "Hemoglobin": {"expected_value": 9.2, "unit": "g/dL"},
                "Glucose": {"expected_value": 185, "unit": "mg/dL"},
                "Albumin": {"expected_value": 2.9, "unit": "g/dL"}
            }
        },
        "classification_ground_truth": {
            "Creatinine": {
                "status": "High",
                "severity": "Critical",
                "rationale": "3.8 mg/dL indicates severe renal impairment"
            },
            "BUN": {
                "status": "High",
                "severity": "Severe",
                "rationale": "68 mg/dL significantly elevated"
            },
            "Potassium": {
                "status": "High",
                "severity": "Critical",
                "rationale": "5.9 mEq/L approaching dangerous hyperkalemia (>6.0)"
            },
            "Sodium": {
                "status": "Low",
                "severity": "Moderate",
                "rationale": "132 mEq/L mild hyponatremia"
            },
            "Hemoglobin": {
                "status": "Low",
                "severity": "Severe",
                "rationale": "9.2 g/dL moderate-to-severe anemia"
            },
            "Glucose": {
                "status": "High",
                "severity": "Severe",
                "rationale": "185 mg/dL uncontrolled diabetes"
            },
            "Albumin": {
                "status": "Low",
                "severity": "Moderate",
                "rationale": "2.9 g/dL hypoalbuminemia (malnutrition/loss)"
            }
        },
        "pattern_ground_truth": {
            "expected_patterns": [
                {
                    "pattern": "Kidney Disease",
                    "confidence": "definitive",
                    "supporting_evidence": ["creatinine 3.8", "BUN 68", "hyperkalemia"]
                },
                {
                    "pattern": "AnChron Disease",
                    "confidence": "high",
                    "supporting_evidence": ["hemoglobin 9.2", "CKD stage 4"]
                },
                {
                    "pattern": "Electrolyte Imbalance",
                    "confidence": "high",
                    "supporting_evidence": ["hyperkalemia", "hyponatremia", "CKD"]
                }
            ],
            "absent_patterns": ["Diabetes Risk", "Liver Dysfunction"]
        },
        "risk_scoring_ground_truth": {
            "cardiovascular": {
                "expected_category": "High",
                "expected_range": {"min": 25, "max": 40},
                "expected_triggers": ["Age >70", "Female", "CKD Stage 4", "Diabetes", "Hypertension"],
                "rationale": "Elderly with stage 4 CKD, diabetes, HTN - very high CV risk"
            }
        },
        "metadata": {
            "annotator": "Clinical expert",
            "annotation_date": "2026-02-13",
            "confidence": "high",
            "notes": "Critical values case - tests severity classification and urgent flag detection"
        }
    }
}


# ===========================================================================
# DATASET STATISTICS
# ===========================================================================

def get_dataset_statistics():
    """Calculate dataset statistics."""
    total_cases = len(GOLD_STANDARD_DATASET)
    total_parameters = sum(
        len(case["extraction_ground_truth"]["parameters"])
        for case in GOLD_STANDARD_DATASET.values()
    )
    
    total_classifications = sum(
        len(case["classification_ground_truth"])
        for case in GOLD_STANDARD_DATASET.values()
    )
    
    total_patterns = sum(
        len(case["pattern_ground_truth"]["expected_patterns"])
        for case in GOLD_STANDARD_DATASET.values()
    )
    
    return {
        "total_test_cases": total_cases,
        "total_parameters": total_parameters,
        "total_classifications": total_classifications,
        "total_patterns": total_patterns,
        "avg_parameters_per_case": total_parameters / total_cases,
        "coverage": {
            "high_risk_cases": 1,
            "low_risk_cases": 1,
            "anemia_cases": 1,
            "diabetes_cases": 1,
            "cardiovascular_cases": 1
        }
    }


# ===========================================================================
# EXPANSION TEMPLATE
# ===========================================================================

def get_expansion_template():
    """
    Template for adding new test cases.
    
    This should be used when expanding the dataset to 50-100 cases.
    """
    return {
        "test_case_N": {
            "patient_id": "TCXXX",
            "description": "Brief clinical description",
            "source_file": "report_file.json",
            "extraction_ground_truth": {
                "parameters": [],
                "total_expected": 0
            },
            "classification_ground_truth": {},
            "pattern_ground_truth": {
                "expected_patterns": [],
                "absent_patterns": []
            },
            "risk_scoring_ground_truth": {
                "cardiovascular": {
                    "expected_category": "Low|Borderline|Intermediate|High",
                    "expected_range": {"min": 0, "max": 100},
                    "rationale": "Clinical reasoning",
                    "expected_triggers": []
                }
            },
            "metadata": {
                "annotator": "Name",
                "annotation_date": "YYYY-MM-DD",
                "confidence": "low|moderate|high",
                "notes": "Additional context"
            }
        }
    }


if __name__ == "__main__":
    # Display dataset statistics
    stats = get_dataset_statistics()
    print("\n" + "="*80)
    print("GOLD STANDARD DATASET STATISTICS")
    print("="*80)
    print(f"\nTotal Test Cases: {stats['total_test_cases']}")
    print(f"Total Parameters: {stats['total_parameters']}")
    print(f"Total Classifications: {stats['total_classifications']}")
    print(f"Total Patterns: {stats['total_patterns']}")
    print(f"Average Parameters per Case: {stats['avg_parameters_per_case']:.1f}")
    print("\n" + "="*80 + "\n")
