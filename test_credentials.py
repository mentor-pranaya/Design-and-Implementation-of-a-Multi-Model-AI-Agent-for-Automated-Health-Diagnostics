import requests

BASE_URL = "http://localhost:10005"

def test_login(username, password, role):
    print(f"Testing login for {username}...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/login/",
            json={"username": username, "password": password, "role": role}
        )
        if response.ok:
            print(f"✅ Login successful for {username}")
            return response.json()['access_token']
        else:
            print(f"❌ Login failed for {username}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return None

# Test Patient Login
test_login("patient", "patient123", "patient")

# Test Admin Login
test_login("admin", "admin123", "admin")
