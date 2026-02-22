# Manual Verification Guide for Ground Truth Annotations

## Overview

This guide provides step-by-step instructions for manually verifying ground truth annotations for the Milestone 1 validation dataset. Manual verification ensures that the automated ground truth templates contain accurate parameter values and classifications before they are used to validate the system's performance.

**Purpose**: Verify that each ground truth JSON file accurately represents the blood test parameters and classifications from the original PDF/PNG reports.

**Target Audience**: Clinical validators, quality engineers, or anyone responsible for ensuring the accuracy of the validation dataset.

**Time Estimate**: 10-15 minutes per report (2-3 hours total for 17 reports)

---

## Prerequisites

Before starting verification, ensure you have:

1. Access to all original test reports in `data/test_reports/`
2. Generated ground truth JSON files in `evaluation/test_dataset/ground_truth/`
3. A PDF viewer (for PDF reports) and image viewer (for PNG reports)
4. A text editor or JSON editor for editing ground truth files
5. Basic understanding of blood test parameters and reference ranges

---

## Verification Workflow

### Step 1: Prepare Your Workspace

1. Open two windows side-by-side:
   - **Left**: PDF/PNG viewer with the original report
   - **Right**: Text editor with the corresponding ground truth JSON file

2. Identify the report pair:
   - Report file: `data/test_reports/report_001.pdf`
   - Ground truth file: `evaluation/test_dataset/ground_truth/report_001.json`

3. Create a verification checklist (optional but recommended):
   ```
   [ ] Report metadata verified
   [ ] All parameters extracted
   [ ] All values correct
   [ ] All units correct
   [ ] All reference ranges correct
   [ ] All classifications correct
   [ ] Notes added (if needed)
   [ ] Marked as verified
   ```

### Step 2: Verify Report Metadata

Open the ground truth JSON file and verify the `report_metadata` section:

```json
"report_metadata": {
  "laboratory": "Lab Name",
  "format": "PDF",
  "date": "2026-01-15",
  "completeness": "Complete",
  "abnormality_type": "Normal",
  "verified": false,
  "verified_by": "",
  "verified_date": ""
}
```

**Verification Steps**:

1. **Laboratory**: Check if the lab name matches the report header
   - If incorrect or missing, update it
   - If not visible in report, use "Unknown"

2. **Format**: Verify it matches the file type (PDF or PNG)
   - Should be "PDF" for .pdf files
   - Should be "PNG" for .png files

3. **Date**: Check if the report date matches
   - Look for "Report Date", "Collection Date", or similar
   - Use format: "YYYY-MM-DD"
   - If not visible, use "Unknown"

4. **Completeness**: Assess if the report is complete
   - "Complete": All sections filled, no missing data
   - "Partial": Some parameters missing or incomplete
   - "Incomplete": Significant data missing

5. **Abnormality Type**: Determine the overall report status
   - "Normal": All parameters within normal ranges
   - "Abnormal": One or more parameters outside normal ranges
   - "Mixed": Some normal, some abnormal

**Do NOT modify** `verified`, `verified_by`, or `verified_date` yet—these will be updated at the end.

### Step 3: Verify Extracted Parameters

Review the `parameters` section, which contains all extracted blood test parameters:

```json
"parameters": {
  "hemoglobin": {
    "value": 14.5,
    "unit": "g/dL",
    "reference_range": {
      "min": 13.0,
      "max": 17.5
    }
  },
  "glucose": {
    "value": 95,
    "unit": "mg/dL",
    "reference_range": {
      "min": 70,
      "max": 100
    }
  }
}
```

**For each parameter, verify**:

#### 3.1 Parameter Name

- Check if the parameter name is standardized and correct
- Common parameters: `hemoglobin`, `glucose`, `creatinine`, `cholesterol`, `triglycerides`, etc.
- If the name is incorrect or non-standard, correct it

#### 3.2 Parameter Value

**Critical Step**: This is the most important verification!

1. Locate the parameter in the original report
2. Compare the extracted value with the printed value
3. Check for common OCR errors:
   - `0` vs `O` (zero vs letter O)
   - `1` vs `l` vs `I` (one vs lowercase L vs uppercase i)
   - `5` vs `S`
   - `8` vs `B`
   - Decimal point misplacement (14.5 vs 145)

**If the value is incorrect**:
```json
"hemoglobin": {
  "value": 14.5,  // Change this to the correct value
  "unit": "g/dL",
  "reference_range": {
    "min": 13.0,
    "max": 17.5
  }
}
```

**Add a note** in the `notes` section:
```json
"notes": "Corrected hemoglobin value from 14.5 to 15.2 (OCR error: 5 read as 2)"
```

#### 3.3 Parameter Unit

Verify the unit matches the report:

- Common units: `g/dL`, `mg/dL`, `mmol/L`, `IU/L`, `µg/dL`, `%`
- Check for unit conversion issues
- Ensure consistency (e.g., don't mix `g/dL` and `g/L`)

**If the unit is incorrect**, update it and add a note.

#### 3.4 Reference Range

Verify the reference range matches what's shown in the report:

```json
"reference_range": {
  "min": 13.0,
  "max": 17.5
}
```

**Important**: The reference range should match what the UnifiedReferenceManager uses, which may be based on:
- Indian population calibration
- Age and gender adjustments
- Laboratory-specific ranges

**If the reference range differs from the report**:
- Check if the system is using Indian population calibration (this is expected)
- If the difference is significant, add a note explaining the discrepancy
- Do NOT change the reference range unless it's clearly wrong

**Example note**:
```json
"notes": "Report shows reference range 12-16 g/dL, but system uses Indian population range 13-17.5 g/dL (this is correct)"
```

### Step 4: Verify Classifications

Review the `classifications` section:

```json
"classifications": {
  "hemoglobin": "Normal",
  "glucose": "High",
  "creatinine": "Low"
}
```

**For each classification, verify**:

1. **Check the classification logic**:
   - **Normal**: Value is within the reference range (min <= value <= max)
   - **High**: Value is above the maximum reference value (value > max)
   - **Low**: Value is below the minimum reference value (value < min)

2. **Verify the math**:
   ```
   Example: Glucose = 110 mg/dL, Range = 70-100 mg/dL
   110 > 100 -> Classification should be "High" [CORRECT]
   ```

3. **Check for edge cases**:
   - Values exactly at the boundary (e.g., value = 100, max = 100)
   - Should be classified as "Normal" (inclusive boundaries)

**If a classification is incorrect**:

```json
"classifications": {
  "glucose": "Normal"  // Change from "High" to "Normal" if incorrect
}
```

**Add a note**:
```json
"notes": "Corrected glucose classification from High to Normal (value 95 is within range 70-100)"
```

### Step 5: Check for Missing Parameters

Compare the ground truth file with the original report to ensure all parameters are captured:

1. Scan the original report for all blood test parameters
2. Check if each parameter appears in the ground truth JSON
3. If a parameter is missing:
   - Add it manually to the `parameters` section
   - Add the corresponding classification
   - Add a note explaining the addition

**Example of adding a missing parameter**:

```json
"parameters": {
  // ... existing parameters ...
  "platelet_count": {
    "value": 250000,
    "unit": "cells/µL",
    "reference_range": {
      "min": 150000,
      "max": 400000
    }
  }
},
"classifications": {
  // ... existing classifications ...
  "platelet_count": "Normal"
},
"notes": "Added missing platelet_count parameter (was not extracted by automated system)"
```

### Step 6: Add Verification Notes

Use the `notes` field to document:

1. **Corrections made**: Any values, units, or classifications you changed
2. **Discrepancies**: Differences between report and system output
3. **Ambiguities**: Unclear values or ranges in the original report
4. **Edge cases**: Borderline values or unusual situations
5. **Missing data**: Parameters that couldn't be extracted

**Example notes**:

```json
"notes": "1. Corrected hemoglobin from 14.5 to 15.2 (OCR error). 2. Glucose value is borderline (95 mg/dL with range 70-100). 3. Report shows fasting glucose, confirmed Normal classification. 4. Added missing platelet_count parameter."
```

### Step 7: Mark as Verified

Once you've completed all verification steps, update the metadata:

```json
"report_metadata": {
  "laboratory": "PathLab",
  "format": "PDF",
  "date": "2026-01-15",
  "completeness": "Complete",
  "abnormality_type": "Normal",
  "verified": true,                    // Change to true
  "verified_by": "Your Name",          // Add your name
  "verified_date": "2026-01-20"        // Add today's date (YYYY-MM-DD)
}
```

### Step 8: Save and Move to Next Report

1. Save the JSON file
2. Validate the JSON syntax (use a JSON validator if needed)
3. Move to the next report and repeat steps 1-7

---

## Common Verification Scenarios

### Scenario 1: OCR Misread a Value

**Problem**: The extracted value doesn't match the report.

**Example**:
- Report shows: `Hemoglobin: 15.2 g/dL`
- Ground truth shows: `"value": 152`

**Solution**:
1. Correct the value: `"value": 15.2`
2. Add note: `"Corrected hemoglobin from 152 to 15.2 (decimal point error)"`

### Scenario 2: Wrong Classification

**Problem**: The classification doesn't match the reference range.

**Example**:
- Value: 95 mg/dL
- Range: 70-100 mg/dL
- Classification: "High" (incorrect)

**Solution**:
1. Correct classification: `"glucose": "Normal"`
2. Add note: `"Corrected glucose classification from High to Normal (95 is within 70-100)"`

### Scenario 3: Missing Parameter

**Problem**: A parameter in the report is not in the ground truth file.

**Example**:
- Report shows: `Platelet Count: 250,000 cells/µL`
- Not in ground truth JSON

**Solution**:
1. Add parameter to `parameters` section
2. Add classification to `classifications` section
3. Add note: `"Added missing platelet_count parameter"`

### Scenario 4: Ambiguous Reference Range

**Problem**: The report shows a different reference range than the system uses.

**Example**:
- Report range: 12-16 g/dL
- System range: 13-17.5 g/dL (Indian population calibration)

**Solution**:
1. Keep the system's reference range (13-17.5)
2. Add note: `"Report shows 12-16 g/dL, system uses Indian population range 13-17.5 g/dL (correct)"`

### Scenario 5: Borderline Value

**Problem**: A value is very close to the reference range boundary.

**Example**:
- Value: 100 mg/dL
- Range: 70-100 mg/dL
- Classification: "Normal"

**Solution**:
1. Verify classification is correct (100 = max, so "Normal")
2. Add note: `"Glucose is at upper boundary (100 mg/dL), classified as Normal (inclusive boundary)"`

### Scenario 6: Unit Mismatch

**Problem**: The unit in the ground truth doesn't match the report.

**Example**:
- Report shows: `Glucose: 5.3 mmol/L`
- Ground truth shows: `"value": 95, "unit": "mg/dL"`

**Solution**:
1. Decide on standard unit (prefer mg/dL for consistency)
2. If conversion is correct (5.3 mmol/L ≈ 95 mg/dL), keep it
3. Add note: `"Report shows 5.3 mmol/L, converted to 95 mg/dL (correct)"`

### Scenario 7: Incomplete Report

**Problem**: The report is missing some parameters or has poor quality.

**Example**:
- Report is a low-quality scan
- Some values are illegible

**Solution**:
1. Extract what you can
2. Update metadata: `"completeness": "Partial"`
3. Add note: `"Some values illegible due to poor scan quality. Extracted 12 of 15 parameters."`

---

## Troubleshooting

### Issue: JSON Syntax Error After Editing

**Symptoms**: File won't save or shows syntax error.

**Common Causes**:
- Missing comma between fields
- Extra comma after last field
- Unmatched quotes or brackets
- Invalid number format

**Solution**:
1. Use a JSON validator (e.g., jsonlint.com)
2. Check for common syntax errors
3. Ensure all strings are in double quotes
4. Ensure numbers don't have quotes

### Issue: Can't Find Parameter in Report

**Symptoms**: Ground truth has a parameter you can't locate in the report.

**Possible Causes**:
- Parameter is on a different page
- Parameter has a different name in the report
- Parameter was incorrectly extracted

**Solution**:
1. Search all pages of the report
2. Look for alternative names (e.g., "HbA1c" vs "Glycated Hemoglobin")
3. If truly not present, remove it and add a note

### Issue: Reference Range Doesn't Match Report

**Symptoms**: System's reference range differs from what's printed on the report.

**Explanation**: This is often expected because:
- System uses Indian population calibration
- System adjusts for age/gender
- System uses more recent clinical guidelines

**Solution**:
1. Keep the system's reference range
2. Add a note explaining the difference
3. Only change if the system's range is clearly wrong

### Issue: Unclear Classification for Borderline Value

**Symptoms**: Value is exactly at the boundary, unclear if Normal or High/Low.

**Rule**: Boundaries are inclusive for Normal range.
- If value = min, classify as "Normal"
- If value = max, classify as "Normal"
- If value < min, classify as "Low"
- If value > max, classify as "High"

**Example**:
- Value: 100, Range: 70-100 -> "Normal" [CORRECT]
- Value: 100.1, Range: 70-100 -> "High" [CORRECT]

---

## Quality Checklist

Before marking a file as verified, ensure:

- [ ] All parameter values match the original report
- [ ] All units are correct and consistent
- [ ] All reference ranges are appropriate
- [ ] All classifications are mathematically correct
- [ ] No parameters are missing from the report
- [ ] No extra parameters that aren't in the report
- [ ] Notes explain any corrections or discrepancies
- [ ] Metadata is complete and accurate
- [ ] JSON syntax is valid
- [ ] File is saved with correct name format

---

## Best Practices

1. **Work in batches**: Verify 3-5 reports at a time, then take a break
2. **Double-check critical values**: Glucose, creatinine, and other clinically significant parameters
3. **Be consistent**: Use the same standards across all reports
4. **Document everything**: When in doubt, add a note
5. **Use a checklist**: Track your progress for each report
6. **Validate JSON**: Always check JSON syntax before saving
7. **Review your work**: After finishing all reports, spot-check a few for quality

---

## File Naming Convention

Ground truth files should follow this naming pattern:

- PDF reports: `report_001.json`, `report_002.json`, etc.
- PNG reports: `report_015_png.json`, `report_016_png.json`, etc.

Ensure the file name matches the original report number.

---

## After Verification

Once all 17 reports are verified:

1. **Count verified files**: Ensure you have 17 JSON files with `"verified": true`
2. **Run validation pipeline**: Execute `python evaluation/run_validation.py`
3. **Review results**: Check the validation report for accuracy metrics
4. **Address errors**: If classification accuracy < 98%, investigate errors
5. **Generate certification**: If targets are met, certification document will be created

---

## Support and Questions

If you encounter issues during verification:

1. **Check this guide**: Review the relevant section
2. **Check the template**: Refer to `evaluation/test_dataset/ground_truth/TEMPLATE.json`
3. **Check the design doc**: See system design documentation
4. **Ask for help**: Contact the development team with specific questions

---

## Summary

Manual verification is a critical step in ensuring the accuracy of the Milestone 1 validation dataset. By carefully comparing each ground truth file against the original reports, you ensure that the system's performance metrics are based on accurate, verified data.

**Key Points**:
- Verify values, units, reference ranges, and classifications
- Correct any errors and document them in notes
- Mark files as verified only when complete
- Maintain consistency across all reports
- Use the quality checklist before finishing each report

**Time Investment**: 2-3 hours for 17 reports
**Impact**: Ensures accurate validation of Milestone 1 targets (>98% classification accuracy)

Good luck with your verification work!
