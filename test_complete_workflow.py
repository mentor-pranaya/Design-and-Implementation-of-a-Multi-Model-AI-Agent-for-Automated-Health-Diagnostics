import requests
import os

BASE_URL = "http://localhost:10005"
API_KEY = "test-key"

headers = {"x-api-key": API_KEY}

# Upload a sample CSV with clear parameters
sample_file = "test_samples/anemic_high_cholesterol.csv"

if os.path.exists(sample_file):
    print(f"Uploading {sample_file}...")
    
    with open(sample_file, "rb") as f:
        files = {"file": (os.path.basename(sample_file), f, "text/csv")}
        response = requests.post(f"{BASE_URL}/analyze-report/", files=files, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        report_id = result.get("report_id")
        print(f"✓ Analysis complete! Report ID: {report_id}")
        print(f"  Summary: {result.get('summary', 'N/A')[:100]}...")
        
        # Download the PDF
        if report_id:
            pdf_response = requests.get(f"{BASE_URL}/report/{report_id}/download", headers=headers)
            if pdf_response.status_code == 200:
                filename = f"enhanced_sample_report_{report_id}.pdf"
                with open(filename, "wb") as f:
                    f.write(pdf_response.content)
                print(f"✓ Enhanced PDF generated: {filename}")
                print(f"  Size: {len(pdf_response.content)} bytes")
                print(f"\nPlease open '{filename}' to review:")
                print("  - Parameter values and interpretations")
                print("  - Health analysis and suggestions")
                print("  - Prescription recommendations")
            else:
                print(f"✗ PDF download failed: {pdf_response.status_code}")
    else:
        print(f"✗ Upload failed: {response.status_code}")
        print(f"  Error: {response.text}")
else:
    print(f"Sample file not found: {sample_file}")
