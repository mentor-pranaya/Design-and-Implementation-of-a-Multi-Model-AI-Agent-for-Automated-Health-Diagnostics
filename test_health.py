import requests
import time
import sys

def test_health():
    url = "http://localhost:10000/health"
    print(f"Testing {url}...")
    
    for i in range(10):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("[OK] Server is UP and Healthy!")
                print("Response:", response.json())
                return True
            else:
                print(f"[FAIL] Server returned status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"[WAIT] Waiting for server... ({e})")
        
        time.sleep(2)
    
    print("[FAIL] Server failed to start in time.")
    return False

if __name__ == "__main__":
    success = test_health()
    sys.exit(0 if success else 1)
