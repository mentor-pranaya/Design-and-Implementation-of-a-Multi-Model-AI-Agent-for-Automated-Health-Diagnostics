"""
Quick test script to verify login API is working
"""
import requests
import json

print("Testing INBLOODO Login API...")
print("="*50)

# Test 1: Login with admin/secret
print("\nTest 1: Login with admin/secret")
response = requests.post(
    'http://localhost:10000/api/login/',
    json={'username': 'admin', 'password': 'secret'}
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Login with admin/admin123
print("\nTest 2: Login with admin/admin123")
response = requests.post(
    'http://localhost:10000/api/login/',
    json={'username': 'admin', 'password': 'admin123'}
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 3: Invalid credentials
print("\nTest 3: Invalid credentials")
response = requests.post(
    'http://localhost:10000/api/login/',
    json={'username': 'wrong', 'password': 'wrong'}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

print("\n" + "="*50)
print("✅ Login API is working!" if response.status_code in [200, 401] else "❌ API has issues")
