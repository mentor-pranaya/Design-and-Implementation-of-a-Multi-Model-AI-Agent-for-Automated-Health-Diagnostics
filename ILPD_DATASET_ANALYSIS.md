# Indian Liver Patient Dataset (ILPD) - Analysis and Integration

**Date:** February 18, 2026  
**Status:** ✅ ANALYZED - RECOMMENDED FOR VALIDATION USE  
**Location:** `ILPD -Indian Liver Patient Dataset/`

---

## 📊 Dataset Overview

**Source:** North East Andhra Pradesh, India  
**Total Records:** 583 individuals  
**Composition:**
- **Healthy Controls:** 167 individuals (28.6%)
- **Liver Patients:** 416 individuals (71.4%)

**Demographics:**
- **Males:** 441 (75.6%)
- **Females:** 142 (24.4%)
- **Age Range:** 4-90 years
- **Mean Age:** 44.5 years (Healthy: 41.2, Liver patients: 46.2)

**Parameters Measured:**
1. Age
2. Gender
3. Total Bilirubin (TB)
4. Direct Bilirubin (DB)
5. Alkaline Phosphatase (Alkphos)
6. ALT/SGPT
7. AST/SGOT
8. Total Protein (TP)
9. Albumin (ALB)
10. A/G Ratio (Albumin/Globulin Ratio)
11. Selector (1=Liver patient, 2=Healthy control)

---

## 🔬 Reference Ranges from Healthy Controls (n=167)

### Overall (Both Genders)
| Parameter | Range (2.5th-97.5th) | Median | Mean | Unit |
|-----------|---------------------|--------|------|------|
| Total Bilirubin | 0.60 - 5.00 | 0.80 | 1.14 | mg/dL |
| Direct Bilirubin | 0.10 - 2.19 | 0.20 | 0.40 | mg/dL |
| Alkaline Phosphatase | 114 - 508 | 186 | 220 | U/L |
| **ALT/SGPT** | **11 - 91** | **27** | **34** | **U/L** |
| **AST/SGOT** | **13 - 134** | **29** | **41** | **U/L** |
| Total Protein | 4.50 - 8.38 | 6.60 | 6.54 | g/dL |
| Albumin | 1.72 - 4.60 | 3.40 | 3.34 | g/dL |
| A/G Ratio | 0.50 - 1.70 | 1.00 | 1.03 | ratio |

### Male (n=117)
| Parameter | Range (2.5th-97.5th) | Median | Mean | Unit |
|-----------|---------------------|--------|------|------|
| Total Bilirubin | 0.60 - 5.35 | 0.80 | 1.24 | mg/dL |
| Direct Bilirubin | 0.10 - 2.37 | 0.20 | 0.45 | mg/dL |
| Alkaline Phosphatase | 113 - 596 | 185 | 227 | U/L |
| **ALT/SGPT** | **12 - 94** | **28** | **35** | **U/L** |
| **AST/SGOT** | **15 - 151** | **30** | **44** | **U/L** |
| Total Protein | 3.90 - 8.20 | 6.50 | 6.53 | g/dL |
| Albumin | 1.69 - 4.51 | 3.50 | 3.34 | g/dL |
| A/G Ratio | 0.50 - 1.72 | 1.00 | 1.04 | ratio |

### Female (n=50)
| Parameter | Range (2.5th-97.5th) | Median | Mean | Unit |
|-----------|---------------------|--------|------|------|
| Total Bilirubin | 0.60 - 2.53 | 0.80 | 0.91 | mg/dL |
| Direct Bilirubin | 0.10 - 1.11 | 0.20 | 0.27 | mg/dL |
| Alkaline Phosphatase | 137 - 410 | 188 | 203 | U/L |
| **ALT/SGPT** | **10 - 83** | **24** | **30** | **U/L** |
| **AST/SGOT** | **12 - 86** | **27** | **32** | **U/L** |
| Total Protein | 4.59 - 8.48 | 6.75 | 6.58 | g/dL |
| Albumin | 1.92 - 4.68 | 3.25 | 3.35 | g/dL |
| A/G Ratio | 0.52 - 1.70 | 1.00 | 1.01 | ratio |

---

## 📈 Comparison with Existing Indian Population Data

### ALT/SGPT - CRITICAL COMPARISON

| Source | Male Range (U/L) | Female Range (U/L) | Sample Size |
|--------|------------------|-------------------|-------------|
| **ILPD Healthy** | 12 - 94 | 10 - 83 | n=167 |
| **Apollo** | 11 - 70 | 9 - 63 | n=10,665 |
| **North Indian** | 10 - 68 | 9 - 63 | n=1,527 |
| **IFCC Hinduja** | 15 - 74 | 10 - 37 | validation |
| **Western Standard** | 0 - 40 | 0 - 40 | - |

**Analysis:**
- ILPD upper limits (M: 94, F: 83) are **HIGHER** than Apollo/North Indian/IFCC
- This is likely due to:
  - Small sample size (n=167 vs n=12,192+)
  - Regional variation (Andhra Pradesh)
  - Possible inclusion of subclinical cases
  - Not designed as reference interval study
- **Recommendation:** Use Apollo + North Indian + IFCC as primary reference (larger, more rigorous)

### AST/SGOT - CRITICAL COMPARISON

| Source | Male Range (U/L) | Female Range (U/L) | Sample Size |
|--------|------------------|-------------------|-------------|
| **ILPD Healthy** | 15 - 151 | 12 - 86 | n=167 |
| **Apollo** | 14 - 42 | 12 - 37 | n=10,665 |
| **North Indian** | 14 - 55 | 13 - 50 | n=1,527 |
| **IFCC Hinduja** | 20 - 53 | 17 - 39 | validation |
| **Western Standard** | 0 - 40 | 0 - 40 | - |

**Analysis:**
- ILPD upper limits (M: 151, F: 86) are **MUCH HIGHER** than other studies
- This suggests:
  - Possible outliers in small sample
  - Regional variation
  - Less rigorous exclusion criteria
- **Recommendation:** Use Apollo + North Indian + IFCC as primary reference

### Total Bilirubin - COMPARISON

| Source | Male Range (mg/dL) | Female Range (mg/dL) | Sample Size |
|--------|-------------------|---------------------|-------------|
| **ILPD Healthy** | 0.60 - 5.35 | 0.60 - 2.53 | n=167 |
| **Apollo** | 0.3 - 1.2 | 0.3 - 1.0 | n=10,665 |
| **North Indian** | 0.4 - 1.34 | 0.3 - 1.2 | n=1,527 |
| **Western Standard** | 0.0 - 1.2 | 0.0 - 1.2 | - |

**Analysis:**
- ILPD male upper limit (5.35) is **MUCH HIGHER** than other studies
- This is a red flag suggesting:
  - Possible subclinical liver disease in "healthy" controls
  - Small sample size amplifying outliers
  - Less rigorous screening
- **Recommendation:** Do NOT use ILPD for bilirubin reference ranges

---

## ⚠️ Limitations of ILPD Dataset

### 1. Small Sample Size
- **Healthy controls:** Only 167 individuals
- **Comparison:** Apollo has 10,665 individuals (64x larger)
- **Impact:** Small samples are more susceptible to outliers and regional variation

### 2. Not Designed as Reference Interval Study
- **Purpose:** Disease classification study, not reference range establishment
- **Exclusion criteria:** Less rigorous than Apollo/IFCC studies
- **Quality control:** Not NABL/ISO 15189 accredited like Apollo

### 3. Regional Dataset
- **Location:** North East Andhra Pradesh only
- **Comparison:** Apollo covers 4 cities, North Indian covers North India, IFCC covers Mumbai
- **Impact:** May not represent broader Indian population

### 4. Possible Subclinical Cases
- **Issue:** "Healthy" controls may include subclinical liver disease
- **Evidence:** Upper limits for ALT, AST, and bilirubin are much higher than other studies
- **Impact:** Would lead to overly permissive reference ranges

### 5. Age Range Issues
- **Range:** 4-90 years (includes children)
- **Comparison:** Apollo/IFCC focus on adults (18-70 years)
- **Impact:** Mixing pediatric and adult ranges is problematic

---

## ✅ Value of ILPD Dataset

Despite limitations, ILPD has significant value:

### 1. Validation Dataset
- **Use:** Test your classification algorithms on real Indian patient data
- **Benefit:** 416 liver patients + 167 healthy controls with known diagnoses
- **Application:** Validate that your system correctly identifies liver disease

### 2. Disease State Comparison
- **Use:** Compare healthy vs diseased ranges
- **Benefit:** Shows how parameters change in liver disease
- **Application:** Helps set appropriate alert thresholds

### 3. Real-World Data
- **Use:** Represents actual clinical data from Indian hospitals
- **Benefit:** More realistic than idealized reference studies
- **Application:** Tests system robustness

### 4. Additional Validation Point
- **Use:** ILPD healthy controls can serve as 4th validation source
- **Benefit:** Confirms existing ranges are reasonable
- **Application:** If ILPD healthy controls fall within Apollo/North Indian/IFCC ranges, it validates those ranges

---

## 💡 Recommended Use in Your System

### ✅ DO USE ILPD FOR:

1. **Validation Testing**
   - Test your system on 167 healthy controls
   - Verify they are correctly classified as "normal"
   - Test your system on 416 liver patients
   - Verify they are correctly flagged for liver issues

2. **Algorithm Testing**
   - Use as test dataset for evaluation
   - Calculate sensitivity/specificity for liver disease detection
   - Validate risk scoring algorithms

3. **Disease State Analysis**
   - Compare healthy vs diseased parameter distributions
   - Validate that your system detects elevated liver enzymes
   - Test alert thresholds

4. **Additional Validation Point**
   - Check if ILPD healthy controls fall within your reference ranges
   - If yes, it validates your ranges
   - If no, investigate why (likely ILPD outliers)

### ❌ DO NOT USE ILPD FOR:

1. **Primary Reference Ranges**
   - Too small (n=167 vs n=12,192+)
   - Not designed for reference intervals
   - Upper limits too high (suggests subclinical cases)

2. **Replacing Existing Data**
   - Apollo + North Indian + IFCC are superior
   - Larger sample sizes
   - More rigorous methodology
   - NABL/ISO/IFCC accredited

3. **Expanding Reference Ranges**
   - ILPD ranges are wider than other studies
   - This would reduce sensitivity for disease detection
   - Would lead to more false negatives

---

## 📋 Integration Recommendation

### Option 1: Use as Validation Dataset (RECOMMENDED)

**Implementation:**
1. Create `evaluation/test_dataset/ilpd/` directory
2. Split ILPD into:
   - `healthy_controls.csv` (167 individuals)
   - `liver_patients.csv` (416 individuals)
3. Use for system validation:
   - Run your system on healthy controls
   - Expected: Most should be classified as "normal"
   - Run your system on liver patients
   - Expected: Most should be flagged for liver issues
4. Calculate metrics:
   - Sensitivity: % of liver patients correctly identified
   - Specificity: % of healthy controls correctly classified
   - Accuracy: Overall correct classification rate

**Benefits:**
- ✅ Provides real-world validation
- ✅ Tests disease detection capability
- ✅ Gives quantitative metrics for internship report
- ✅ Doesn't compromise reference range quality

### Option 2: Document as Additional Data Source

**Implementation:**
1. Add ILPD to documentation
2. Note as "validation dataset" not "reference range source"
3. Include in literature review section
4. Reference in internship report

**Benefits:**
- ✅ Shows thorough data collection
- ✅ Demonstrates critical evaluation of data quality
- ✅ No implementation effort

### Option 3: Do Not Use

**Rationale:**
- Small sample size
- Questionable quality
- Doesn't add value over existing data

---

## 🎯 Recommended Action: Option 1

**Use ILPD as validation dataset to test your system's disease detection capability.**

### Implementation Steps:

1. **Create validation script:**
```python
# evaluation/validate_with_ilpd.py
import pandas as pd
from core_phase3.orchestrator import MultiModelOrchestrator

# Load ILPD data
ilpd = pd.read_csv('ILPD -Indian Liver Patient Dataset/Indian Liver Patient Dataset (ILPD).csv')

# Separate healthy and diseased
healthy = ilpd[ilpd['Selector'] == 2]
diseased = ilpd[ilpd['Selector'] == 1]

# Test system on healthy controls
# Expected: Most classified as "normal" or "low risk"

# Test system on liver patients
# Expected: Most flagged for elevated liver enzymes

# Calculate sensitivity, specificity, accuracy
```

2. **Add to evaluation framework:**
   - Include ILPD validation in `evaluation/evaluate_milestone1.py`
   - Report metrics in evaluation results

3. **Document in internship report:**
   - "System validated on 583 real-world Indian patients"
   - "Achieved X% sensitivity for liver disease detection"
   - "Achieved Y% specificity (correct classification of healthy controls)"

---

## 📊 Expected Validation Results

### Healthy Controls (n=167)
**Expected Classification:**
- Most should be classified as "normal" or "low risk"
- Some may be flagged due to:
  - Age-related variations
  - Regional variations
  - Possible subclinical cases in dataset

**Success Criteria:**
- ≥80% classified as "normal" or "low risk"
- If lower, investigate why (may reveal system issues or dataset issues)

### Liver Patients (n=416)
**Expected Classification:**
- Most should be flagged for elevated liver enzymes
- Should trigger alerts for:
  - High ALT/SGPT
  - High AST/SGOT
  - High bilirubin
  - Low albumin

**Success Criteria:**
- ≥90% correctly identified as having liver issues
- If lower, investigate why (may reveal system sensitivity issues)

---

## 📁 File Locations

### Dataset:
- `ILPD -Indian Liver Patient Dataset/Indian Liver Patient Dataset (ILPD).csv`
- `ILPD -Indian Liver Patient Dataset/Description.txt`

### Analysis:
- `analyze_ilpd_dataset.py` (analysis script)
- `ILPD_DATASET_ANALYSIS.md` (this document)

### Recommended Integration:
- `evaluation/test_dataset/ilpd/` (create this directory)
- `evaluation/validate_with_ilpd.py` (create validation script)

---

## 📚 Academic Value

### For Your Internship Report:

**Strengths to Highlight:**
1. ✅ Thorough data collection (4 sources: Apollo, North Indian, IFCC, ILPD)
2. ✅ Critical evaluation of data quality
3. ✅ Appropriate use of each dataset (reference vs validation)
4. ✅ Real-world validation on 583 Indian patients
5. ✅ Quantitative validation metrics

**How to Present:**
- "Collected and evaluated 4 Indian population datasets"
- "Selected Apollo + North Indian + IFCC (n=12,192+) as primary reference ranges based on sample size, methodology, and quality standards"
- "Used ILPD (n=583) as validation dataset to test disease detection capability"
- "Achieved X% sensitivity and Y% specificity on real-world Indian patient data"

---

## ✅ Summary

**ILPD Dataset:**
- 583 individuals (167 healthy, 416 liver patients)
- North East Andhra Pradesh, India
- 8 liver-related parameters

**Recommendation:**
- ✅ **USE** as validation dataset
- ❌ **DO NOT USE** as primary reference range source

**Rationale:**
- Small sample size (n=167 vs n=12,192+)
- Not designed for reference intervals
- Upper limits too high (suggests subclinical cases)
- Better suited for testing disease detection

**Value:**
- Provides real-world validation
- Tests disease detection capability
- Gives quantitative metrics for report
- Demonstrates thorough data evaluation

**Next Steps:**
1. Create validation script
2. Test system on ILPD data
3. Calculate sensitivity/specificity
4. Document results in internship report

---

**Generated:** February 18, 2026  
**Status:** ✅ ANALYZED  
**Recommendation:** Use as validation dataset (Option 1)  
**Primary Reference Ranges:** Apollo + North Indian + IFCC (n=12,192+)  
**Validation Dataset:** ILPD (n=583)

