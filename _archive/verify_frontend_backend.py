import requests
import os

BASE_URL = "http://localhost:10000"

def test_frontend_backend():
    print("=== Testing Frontend/Backend Integration ===")
    
    # 1. Check Login Page
    try:
        print("\n1. Checking /login page...")
        resp = requests.get(f"{BASE_URL}/login")
        if resp.status_code == 200:
            print("âœ… Login page is accessible (200 OK)")
            if "Login" in resp.text or "Sign In" in resp.text:
                print("   Found generic login text.")
        else:
            print(f"âŒ Login page failed: {resp.status_code}")
    except Exception as e:
        print(f"âŒ Connection failed: {e}")
        return

    # 2. Check Homepage (without auth, might work or redirect?)
    # api_optimized.py says it just serves index.html, JS handles redirect.
    try:
        print("\n2. Checking / homepage...")
        resp = requests.get(f"{BASE_URL}/")
        if resp.status_code == 200:
            print("âœ… Homepage is accessible (200 OK)")
            if "INBLOODO AGENT" in resp.text:
                print("   Found 'INBLOODO AGENT' in title.")
        else:
            print(f"âŒ Homepage failed: {resp.status_code}")
    except Exception as e:
        print(f"âŒ Connection failed: {e}")

    # 3. Simulate Login API
    try:
        print("\n3. Testing API Login...")
        login_data = {"username": "admin", "password": "admin123"}
        resp = requests.post(f"{BASE_URL}/api/login/", json=login_data)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            print(f"âœ… Login successful! Token: {token}")
            
            # 4. Simulate Upload with Token
            print("\n4. Testing File Upload (Standard Report)...")
            file_path = os.path.join("test_samples", "standard_report.pdf")
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    files = {"file": ("standard_report.pdf", f, "application/pdf")}
                    headers = {"x-api-key": token} # JS uses x-api-key header with session token
                    resp = requests.post(f"{BASE_URL}/analyze-report/", files=files, headers=headers)
                    
                    if resp.status_code == 200:
                        print("âœ… Upload & Analysis successful (200 OK)")
                        print(f"   Risk: {resp.json().get('overall_risk')}")
                    else:
                        print(f"âŒ Upload failed: {resp.status_code}")
                        print(resp.text[:200])
            else:
                print("âš  Skipping upload test (standard_report.pdf not found)")
                
        else:
            print(f"âŒ Login failed: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"âŒ API test failed: {e}")

if __name__ == "__main__":
    test_frontend_backend()
