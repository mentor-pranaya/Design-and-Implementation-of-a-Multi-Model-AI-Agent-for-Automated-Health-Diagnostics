import requests
import os
import glob

URL = "http://localhost:10000/analyze-report/"
API_KEY = "secret"
SAMPLES_DIR = "test_samples"

def test_uploads():
    files = glob.glob(os.path.join(SAMPLES_DIR, "*"))
    print(f"Found {len(files)} sample files to test.")
    print("========================================")
    
    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"\nTesting: {filename}")
        
        # Determine mime type (simple)
        mime_type = 'application/octet-stream'
        if filename.endswith('.pdf'): mime_type = 'application/pdf'
        elif filename.endswith('.png'): mime_type = 'image/png'
        elif filename.endswith('.json'): mime_type = 'application/json'
        elif filename.endswith('.csv'): mime_type = 'text/csv'
        elif filename.endswith('.txt'): mime_type = 'text/plain'
        
        try:
            with open(filepath, "rb") as f:
                # The mime_type determination logic here is slightly different from the one above.
                # The one above is more comprehensive, so we'll use that one.
                # mime_type = "application/json" if filename.endswith(".json") else "application/octet-stream"
                
                if filename.endswith(".csv"):
                    files_dict = {'file': (filename, f, 'text/csv')}
                    response = requests.post(URL, files=files_dict, headers={'x-api-key': API_KEY}, timeout=30)
                elif filename.endswith(".json"):
                    # Send as file upload for consistency with API
                    files_dict = {'file': (filename, f, 'application/json')}
                    response = requests.post(URL, files=files_dict, headers={'x-api-key': API_KEY}, timeout=10)
                else:
                    files_dict = {'file': (filename, f, mime_type)}
                    response = requests.post(URL, files=files_dict, headers={'x-api-key': API_KEY}, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   [SUCCESS] 200 OK")
                print(f"   Extracted: {len(result.get('extracted_parameters', {}))} parameters")
                print(f"   Risk: {result.get('overall_risk')}")
                if result.get('overall_risk'):
                    print(f"   Summary: {result.get('summary', '')[:100]}...")
            else:
                print(f"   [FAILED] Status Code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        
        except Exception as e:
            print(f"   [ERROR] Exception: {str(e)}")

if __name__ == "__main__":
    test_uploads()
