import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY", "your-secure-api-key-here")
base_url = "http://localhost:10000"
headers = {"x-api-key": api_key}

def test_endpoint(endpoint):
    print(f"\nTesting {endpoint}...")
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        if response.status_code == 200:
            print(f"SUCCESS: {endpoint}")
            # print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"FAILED: {endpoint} (Status: {response.status_code})")
            print(response.text)
            return False
    except Exception as e:
        print(f"ERROR: {endpoint} - {str(e)}")
        return False

def verify_all():
    endpoints = [
        "/api/telemetry",
        "/api/analytics/summary",
        "/api/analytics/trends?parameter=glucose&limit=5"
    ]
    
    results = [test_endpoint(e) for e in endpoints]
    
    if all(results):
        print("\nAll dashboard backend endpoints are OPERATIONAL! \u2705")
    else:
        print("\nSome endpoints FAILED. Please check the logs. \u274c")

if __name__ == "__main__":
    verify_all()
