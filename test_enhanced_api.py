import requests
import json

# Test the enhanced API functionality
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "secret"

def test_json_upload():
    """Test API with JSON data upload"""
    url = f"{BASE_URL}/analyze-report/"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # Sample blood report data
    test_data = {
        "hemoglobin": 12.5,
        "glucose": 95,
        "hba1c": 5.8,
        "cholesterol": 220,
        "creatinine": 1.1,
        "alt": 45,
        "wbc": 8500
    }

    try:
        response = requests.post(url, json=test_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response Successful!")
            print(f"Extracted Parameters: {len(result.get('extracted_parameters', {}))}")
            print(f"Precautions: {len(result.get('precautions', []))}")
            print(f"Description: {result.get('description', '')[:100]}...")
            print(f"Risk: {result.get('risk', '')}")
            return True
        else:
            print(f"❌ API Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_file_upload():
    """Test API with file upload"""
    url = f"{BASE_URL}/analyze-report/"
    headers = {"x-api-key": API_KEY}

    try:
        with open("data/sample_report/report.pdf", "rb") as f:
            files = {"file": ("report.pdf", f, "application/pdf")}
            response = requests.post(url, files=files, headers=headers)
            print(f"File Upload Status Code: {response.status_code}")
            if response.status_code == 200:
                print("✅ File Upload Successful!")
                return True
            else:
                print(f"❌ File Upload Error: {response.text}")
                return False
    except FileNotFoundError:
        print("❌ Sample PDF file not found")
        return False
    except Exception as e:
        print(f"❌ File Upload Connection Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Enhanced Blood Report AI API")
    print("=" * 50)

    # Test JSON upload
    print("\n1. Testing JSON Data Upload:")
    json_success = test_json_upload()

    # Test file upload
    print("\n2. Testing File Upload:")
    file_success = test_file_upload()

    print("\n" + "=" * 50)
    if json_success or file_success:
        print("✅ API Testing Completed Successfully!")
    else:
        print("❌ All API Tests Failed")
