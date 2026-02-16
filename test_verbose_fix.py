import requests
import os
import time
import json
import sys

# Force UTF-8 for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:10003"
API_KEY = "test-key"

headers = {
    "X-API-Key": API_KEY,
    "Authorization": f"Bearer {API_KEY}"
}

def test_verbose():
    print("--- Starting Verbose Multi-Format Test ---")
    
    # 1. Test TXT PDF Download specifically
    # rid = 91 # From previous run
    # Actually let's just do a fresh TXT upload
    print("\nProcessing diabetic.txt...")
    files = {'file': ('diabetic.txt', "Glucose: 150 mg/dL\nHgA1c: 7.2%\nWeight: 85kg\nBP: 140/90", 'text/plain')}
    response = requests.post(f"{BASE_URL}/analyze-report/", headers=headers, files=files)
    
    if response.status_code == 200:
        res = response.json()
        rid = res.get("report_id")
        print(f"Success! Report ID: {rid}")
        print(f"Summary: {res.get('summary')}")
        
        if rid:
            print(f"\nAttempting PDF download for ID {rid}...")
            pdf_res = requests.get(f"{BASE_URL}/report/{rid}/download", headers=headers)
            if pdf_res.status_code == 200:
                print("PDF Download Success!")
            else:
                print(f"PDF Download FAILED ({pdf_res.status_code})")
                print(f"ERROR DETAIL: {json.dumps(pdf_res.json(), indent=2)}")
    else:
        print(f"Analysis FAILED ({response.status_code})")
        print(f"ERROR DETAIL: {response.text}")

if __name__ == "__main__":
    test_verbose()
