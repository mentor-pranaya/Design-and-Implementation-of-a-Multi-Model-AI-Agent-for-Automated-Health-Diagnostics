import requests
import sys

URL = "http://localhost:10000/api/login"
CREDENTIALS = {"username": "admin", "password": "admin123"}

try:
    print(f"Testing login at {URL}...")
    response = requests.post(URL, json=CREDENTIALS)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\nSUCCESS: Login verified!")
        token = response.json().get("access_token")
        print(f"Token received: {token[:10]}...")
    else:
        print("\nFAILURE: Login failed.")
        sys.exit(1)

except Exception as e:
    print(f"\nERROR: Could not connect to server. Is it running? {e}")
    sys.exit(1)
