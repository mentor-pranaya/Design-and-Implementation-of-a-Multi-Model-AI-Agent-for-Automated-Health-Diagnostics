import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY", "your-secure-api-key-here")

def test_analysis():
    url = "http://localhost:10000/analyze-json/"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    # Sample blood report data
    data = {
        "Hemoglobin": 11.5,
        "RBC": 4.5,
        "WBC": 12000,
        "Platelets": 250000,
        "Glucose": 110
    }
    
    print(f"Testing Analysis API: {url}")
    print(f"Input Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("\n[SUCCESS] Analysis Complete!")
            print(f"Processing Time: {result.get('processing_time')}s")
            print(f"From Cache: {result.get('from_cache')}")
            
            print("\n--- Recommendations ---")
            for rec in result.get('recommendations', []):
                try:
                    print(f"- {rec.encode('cp1252', errors='ignore').decode('cp1252')}")
                except:
                    print(f"- {rec.encode('ascii', errors='ignore').decode('ascii')}")
                
            print("\n--- Summary ---")
            try:
                print(result.get('summary', '').encode('cp1252', errors='ignore').decode('cp1252'))
            except:
                print(result.get('summary', ''))
            return True
        else:
            print(f"\n[FAIL] Status Code: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Request failed: {e}")
        return False

if __name__ == "__main__":
    test_analysis()
