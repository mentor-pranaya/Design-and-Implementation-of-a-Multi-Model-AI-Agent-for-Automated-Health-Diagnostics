# Testing Instructions - Hormone Parameters Fix

## Current Status
[COMPLETE] Backend server running on port 8000 (auto-reloaded with all changes)
[COMPLETE] Frontend server running on port 3000
[COMPLETE] Hormone parameters added to reference database
[COMPLETE] PDF parsing improved
[COMPLETE] Patient info extraction implemented
[COMPLETE] Reference range display fixed

## Test the Demo PDF

### Step 1: Access the Application
Open your browser and go to: http://localhost:3000

### Step 2: Upload the Demo PDF
1. Click on the upload area or drag-and-drop your PDF
2. The PDF should be: 19 Y / Female, NEETHI LAB - KALAMASSERY
3. Wait for processing to complete (should take 5-10 seconds)

### Step 3: Verify Results

#### Expected Parameter Classifications:

1. **Free T4: 1.36 ng/dL**
   - Classification: Normal [CORRECT]
   - Reference Range: 0.8 - 2.0 ng/dL
   - Status: Green badge

2. **TSH: 1.010 uIU/ml**
   - Classification: Normal [CORRECT]
   - Reference Range: 0.4 - 4.0 mIU/L
   - Status: Green badge

3. **FSH: 7.07 mIU/mL**
   - Classification: Normal [CORRECT]
   - Reference Range: 3.5 - 12.5 mIU/mL (Follicular Phase)
   - Status: Green badge

4. **LH: 14.26 mIU/mL**
   - Classification: High [WARNING]
   - Reference Range: 2.4 - 12.6 mIU/mL (Follicular Phase)
   - Status: Red badge
   - Note: Value is above the upper limit

5. **Prolactin: 53.77 ng/ml**
   - Classification: High [WARNING]
   - Reference Range: 4.79 - 23.3 ng/mL (Non-pregnant Female)
   - Status: Red badge
   - Note: Value is significantly above the upper limit

6. **Testosterone Total: 0.417 ng/ml**
   - Classification: Normal [CORRECT]
   - Reference Range: 0.084 - 0.481 ng/mL (Female)
   - Status: Green badge

### Step 4: Verify Health Risk Assessment

The Health Risk Assessment section should show:
- **Overall Risk Level**: Should be displayed clearly (Low/Moderate/High/Critical)
- **Risk Score**: Displayed as "X/100" format
- **Category Scores**: Cardiovascular, Metabolic, Kidney scores with "/100" suffix
- **Risk Level Legend**: Explaining score ranges

### Step 5: Check for Issues

If you see any of these issues, report them:
- [ERROR] Parameters showing "Unknown" classification
- [ERROR] Reference ranges showing "0 - 0"
- [ERROR] LH or Prolactin not marked as "High"
- [ERROR] Wrong values extracted (e.g., Free T4 showing "4" instead of "1.36")
- [ERROR] Patient info not extracted (should be 19 Y Female)

## Debugging

### Check Backend Logs
If something doesn't work, check the backend terminal for errors:
- Look for "ERROR processing report" messages
- Check if parameters were extracted correctly
- Verify patient info was extracted

### Check Frontend Console
Open browser DevTools (F12) and check the Console tab:
- Look for API errors
- Check if data is being received correctly

### Manual API Test
You can test the API directly:

```bash
# Check if server is running
curl http://localhost:8000/

# Upload a file (replace with your file path)
curl -X POST http://localhost:8000/api/reports/upload -F "file=@path/to/your/file.pdf"

# Check report status (replace {report_id} with actual ID)
curl http://localhost:8000/api/reports/{report_id}/status

# Get report data
curl http://localhost:8000/api/reports/{report_id}
```

## Expected Behavior Summary

[COMPLETE] All 6 hormone parameters should be recognized
[COMPLETE] Sex-specific reference ranges should be used (Female ranges)
[COMPLETE] LH and Prolactin should be marked as "High" (red badge)
[COMPLETE] Free T4, TSH, FSH, and Testosterone should be marked as "Normal" (green badge)
[COMPLETE] Reference ranges should display correctly (not "0 - 0")
[COMPLETE] Health risk assessment should be clear and understandable

## Next Steps After Testing

If everything works:
1. Test with other PDF files to ensure robustness
2. Test with JSON/CSV files to ensure backward compatibility
3. Consider adding more hormone parameters if needed
4. Consider adding menstrual cycle phase selection for more accurate female hormone ranges

If issues persist:
1. Check the backend logs for specific errors
2. Verify the PDF text extraction is working correctly
3. Check if the reference ranges are being loaded properly
4. Verify the API is parsing the reference ranges correctly
