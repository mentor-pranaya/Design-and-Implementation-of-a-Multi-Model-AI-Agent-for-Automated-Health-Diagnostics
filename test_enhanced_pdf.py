import requests

# Test PDF generation for the latest report
BASE_URL = "http://localhost:10005"
API_KEY = "test-key"

headers = {"x-api-key": API_KEY}

# Get the latest report ID from database
import sqlite3
conn = sqlite3.connect('health_reports.db')
cursor = conn.cursor()
cursor.execute('SELECT id FROM reports ORDER BY id DESC LIMIT 1')
report_id = cursor.fetchone()[0]
conn.close()

print(f"Testing PDF generation for Report ID: {report_id}")

# Download PDF
response = requests.get(f"{BASE_URL}/report/{report_id}/download", headers=headers)

if response.status_code == 200:
    filename = f"test_enhanced_report_{report_id}.pdf"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"✓ PDF generated successfully: {filename}")
    print(f"  Size: {len(response.content)} bytes")
else:
    print(f"✗ PDF generation failed: {response.status_code}")
    print(f"  Error: {response.text}")
