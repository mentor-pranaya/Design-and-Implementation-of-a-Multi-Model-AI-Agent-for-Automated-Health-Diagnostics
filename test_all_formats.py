import requests
import os
import time
import json
import sys

# Force UTF-8 for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:10005"
API_KEY = "test-key" # Default key for testing

headers = {
    "x-api-key": API_KEY
}

test_files = [
    ("standard_report.pdf", "application/pdf"),
    ("critical_image.png", "image/png"),
    ("anemic_high_cholesterol.csv", "text/csv"),
    ("normal.json", "application/json"),
    ("diabetic.txt", "text/plain")
]

def test_multi_format():
    report_ids = []
    print("--- Starting Multi-Format Analysis Test ---")
    
    for filename, mime_type in test_files:
        filepath = os.path.join("test_samples", filename)
        if not os.path.exists(filepath):
            print(f"Skipping missing file: {filepath}")
            continue
            
        print(f"\nProcessing {filename}...")
        with open(filepath, "rb") as f:
            files = {"file": (filename, f, mime_type)}
            response = requests.post(f"{BASE_URL}/analyze-report/", files=files, headers=headers)
            
        if response.status_code == 200:
            result = response.json()
            report_id = result.get("report_id")
            report_ids.append(report_id)
            print(f"Success! Report ID: {report_id}")
            if result.get("persistence_error"):
                print(f"   ⚠️ Persistence Error: {result['persistence_error']}")
            
            if report_id is None:
                print(f"   DEBUG: Full Response: {json.dumps(result, indent=2)}")
            else:
                print(f"   Summary: {result.get('summary', 'No summary')[:100]}...")
        else:
            print(f"Failed to process {filename}: {response.status_code} - {response.text}")

    # Verify via Admin API
    print("\n--- Verifying Admin Access ---")
    admin_headers = headers.copy()
    admin_response = requests.get(f"{BASE_URL}/api/admin/reports", headers=admin_headers)
    
    if admin_response.status_code == 200:
        reports = admin_response.json()
        print(f"Admin found {len(reports)} total reports in database.")
        
        # Check if our new reports are there
        found_count = 0
        for rid in report_ids:
            if rid is not None and any(r["id"] == rid for r in reports):
                found_count += 1
                
        print(f"Admin verified {found_count}/{len(report_ids)} newly created reports.")
    else:
        print(f"Admin API failed: {admin_response.status_code}")
        print(f"   Error: {admin_response.text}")

    # Verify PDF Download for the last report
    if report_ids:
        last_id = report_ids[-1]
        print(f"\n--- Verifying PDF Report Generation for ID {last_id} ---")
        pdf_response = requests.get(f"{BASE_URL}/report/{last_id}/download", headers=headers)
        if pdf_response.status_code == 200 and len(pdf_response.content) > 0:
            print(f"PDF downloaded successfully ({len(pdf_response.content)} bytes)")
            with open(f"final_test_report_{last_id}.pdf", "wb") as f:
                f.write(pdf_response.content)
            print(f"Saved to final_test_report_{last_id}.pdf for manual check.")
        else:
            print(f"PDF download failed for ID {last_id}")

if __name__ == "__main__":
    test_multi_format()
