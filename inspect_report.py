import sqlite3
import json

# Connect to database
conn = sqlite3.connect('health_reports.db')
cursor = conn.cursor()

# Get the most recent report
cursor.execute('SELECT id, filename, full_results FROM reports ORDER BY id DESC LIMIT 1')
row = cursor.fetchone()

if row:
    report_id, filename, full_results = row
    print(f"Report ID: {report_id}")
    print(f"Filename: {filename}")
    print("\nFull Results Structure:")
    
    if full_results:
        data = json.loads(full_results)
        print(f"Status: {data.get('status')}")
        print(f"\nExtracted Parameters: {json.dumps(data.get('extracted_parameters', {}), indent=2)}")
        print(f"\nInterpretations: {json.dumps(data.get('interpretations', []), indent=2)}")
        print(f"\nRisks: {json.dumps(data.get('risks', []), indent=2)}")
        print(f"\nRecommendations: {json.dumps(data.get('recommendations', []), indent=2)}")
        print(f"\nLinked Recommendations: {json.dumps(data.get('linked_recommendations', []), indent=2)}")
        print(f"\nPrescriptions: {json.dumps(data.get('prescriptions', []), indent=2)}")
    else:
        print("No full_results data found!")
else:
    print("No reports found in database")

conn.close()
