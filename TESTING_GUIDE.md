# Blood Report Analysis System - Testing Guide

## System Status [COMPLETE]

Both servers are now running with the integrated pipeline:

- **Frontend UI**: http://localhost:3000/
- **Backend API**: http://localhost:8000/

## What's New

The backend now uses the **real blood report processing pipeline** (Phases 1-3):
- Phase 1: File ingestion and parameter extraction
- Phase 3: Evaluation against reference ranges, pattern detection, and personalized recommendations

## How to Test

### 1. Upload a Blood Report

**Option A: Use the test file (Recommended)**
- A test file `test_report.json` has been created in the project root
- Contains 8 blood parameters with various abnormal values

**Option B: Create your own JSON file**
```json
{
  "Hemoglobin": "12.5 g/dL",
  "Glucose": "128 mg/dL",
  "HbA1c": "6.2 %",
  "Total Cholesterol": "220 mg/dL",
  "LDL": "165 mg/dL",
  "HDL": "38 mg/dL",
  "Triglycerides": "180 mg/dL",
  "Creatinine": "1.2 mg/dL"
}
```

### 2. Test Steps

1. **Open the UI**: Navigate to http://localhost:3000/
2. **Go to Upload Page**: Click "Upload" in the navigation bar
3. **Upload File**: 
   - Drag and drop `test_report.json` or click to browse
   - Watch the upload progress
4. **View Processing**: 
   - The system will show processing status
   - Wait for completion (should take a few seconds)
5. **View Results**: 
   - You'll be redirected to the report details page
   - See parameter evaluations with classifications (Normal/High/Low)
   - View health risk scores
   - Read personalized recommendations

### 3. What to Expect

Based on the test data, you should see:

**Parameters Evaluated**: 8 parameters
- Hemoglobin: **Low** (12.5 g/dL)
- Glucose: **High** (128 mg/dL)
- HbA1c: **High** (6.2%)
- Total Cholesterol: **High** (220 mg/dL)
- LDL: **High** (165 mg/dL)
- HDL: **Low** (38 mg/dL)
- Triglycerides: **High** (180 mg/dL)
- Creatinine: Normal or slightly elevated

**Detected Patterns**:
- Anemia Indicator
- Diabetes Risk / Prediabetes Risk
- High Cholesterol
- Metabolic Syndrome

**Health Risk Score**: Critical (96/100)

**Recommendations**: 
- Dietary guidance for each condition
- Exercise plans
- Lifestyle modifications

### 4. Backend Logs

The backend console will show detailed processing logs:
```
======================================================================
Processing report: [report-id]
File: uploads/[filename]
======================================================================
Phase 1: Loading file...
[COMPLETE] Loaded 8 parameters
Phase 1: Extracting parameters...
[COMPLETE] Extracted 8 parameters
Phase 3: Running evaluation pipeline...
[COMPLETE] Phase 3 pipeline complete
Converting to API format...
[COMPLETE] Report data generated with 8 parameters
[COMPLETE] Report [report-id] processing complete
======================================================================
```

### 5. Troubleshooting

**If upload fails:**
- Check backend console for error messages
- Ensure the file format is correct (JSON with parameter: value pairs)
- Verify both servers are running

**If "Invalid API response format" error:**
- This has been fixed in the latest version
- The backend now returns properly formatted responses

**If processing takes too long:**
- Check backend logs for errors
- The Phase 3 pipeline initialization takes a few seconds on first run

## Additional Test Files

You can create more test files with different parameters:

**Normal Report** (all values normal):
```json
{
  "Hemoglobin": "15.0 g/dL",
  "Glucose": "90 mg/dL",
  "Total Cholesterol": "180 mg/dL"
}
```

**Critical Report** (severe abnormalities):
```json
{
  "Hemoglobin": "8.0 g/dL",
  "Glucose": "250 mg/dL",
  "Creatinine": "3.5 mg/dL"
}
```

## System Architecture

```
User Upload (JSON/CSV/PDF)
    then
Phase 1: Ingestion & Extraction
    then
Phase 3A: Reference-Based Evaluation
    then
Phase 3B: Pattern Recognition
    then
Phase 3C: Recommendation Generation
    then
API Response (formatted for UI)
    then
Frontend Visualization
```

## Notes

- Authentication is temporarily disabled for development
- All reports use default patient info (Male, 35 years old)
- PDF support requires OCR dependencies (currently optional)
- The system uses authoritative ABIM reference ranges

Enjoy testing!
