import asyncio
import sys
import os
import requests
import json
import time

# Add src to path
sys.path.append(os.getcwd())

async def verify_final_workflow():
    print("--- Verifying Final Workflow (End-to-End Analysis & Download) ---")
    
    BASE_URL = "http://localhost:10000"
    API_KEY = "test-key" # Assuming this is the key in .env or hardcoded for testing
    
    # 1. Login or get credentials (simplified for test)
    headers = {"x-api-key": API_KEY}
    
    # 2. Test Analyze Report
    print("Step 1: Testing /analyze-report/ with sample data...")
    test_file_path = "test_samples/sample_report.txt"
    
    # Create test samples if they don't exist
    if not os.path.exists("test_samples"):
        os.makedirs("test_samples")
    if not os.path.exists(test_file_path):
        with open(test_file_path, "w") as f:
            f.write("Glucose: 150 mg/dL, Cholesterol: 220 mg/dL")

    try:
        with open(test_file_path, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/analyze-report/",
                files={"file": (os.path.basename(test_file_path), f, "text/plain")},
                headers=headers
            )
        
        if response.status_code == 200:
            result = response.json()
            report_id = result.get("report_id")
            print(f"[PASS] Analysis successful. Report ID: {report_id}")
            
            if report_id:
                # 3. Test PDF Download
                print(f"Step 2: Testing /report/{report_id}/download...")
                download_resp = requests.get(
                    f"{BASE_URL}/report/{report_id}/download",
                    headers=headers
                )
                
                if download_resp.status_code == 200 and len(download_resp.content) > 0:
                    print(f"[PASS] PDF Download successful. Size: {len(download_resp.content)} bytes")
                    # Save a copy for manual inspection
                    with open("verified_report.pdf", "wb") as f:
                        f.write(download_resp.content)
                    print("Verification successful. Check verified_report.pdf")
                else:
                    print(f"[FAIL] PDF Download failed. Status: {download_resp.status_code}")
        else:
            print(f"[FAIL] Analysis failed. Status: {response.status_code}, Body: {response.text}")
            print("Note: Ensure the server (main.py) is running locally!")
            
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")

if __name__ == "__main__":
    # This script requires the server to be running.
    # For CI/unit testing, we'd use TestClient, but for end-to-end, we check the running service.
    asyncio.run(verify_final_workflow())
