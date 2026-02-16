import sqlite3
import json
from datetime import datetime

print("\n" + "=" * 80)
print(" " * 20 + "INBLOODO AI - REPORT HISTORY")
print("=" * 80)

conn = sqlite3.connect('health_reports.db')
cursor = conn.cursor()

# Get total count
cursor.execute('SELECT COUNT(*) FROM reports')
total = cursor.fetchone()[0]

print(f"\n📊 TOTAL RECORDS: {total} reports")
print("=" * 80)

# Get all reports with details
cursor.execute('''
    SELECT id, filename, created_at, description, full_results 
    FROM reports 
    ORDER BY id DESC
''')

print(f"\n{'ID':<5} {'Filename':<30} {'Date':<20} {'Status':<15} {'Parameters':<12}")
print("-" * 80)

success_count = 0
failed_count = 0

for row in cursor.fetchall():
    report_id, filename, created_at, description, full_results = row
    
    # Determine status
    if full_results:
        data = json.loads(full_results)
        status = data.get('status', 'unknown')
        param_count = len(data.get('extracted_parameters', {}))
        
        if status == 'success' or param_count > 0:
            status_display = "✓ Success"
            success_count += 1
        else:
            status_display = "✗ Failed"
            failed_count += 1
    else:
        status_display = "⚠ No Data"
        param_count = 0
        failed_count += 1
    
    # Format date
    date_str = created_at[:16] if created_at else "N/A"
    
    # Truncate filename
    filename_short = (filename[:27] + "...") if filename and len(filename) > 30 else (filename or "Unknown")
    
    print(f"{report_id:<5} {filename_short:<30} {date_str:<20} {status_display:<15} {param_count:<12}")

print("=" * 80)
print(f"\n📈 SUMMARY:")
print(f"  ✓ Successful Reports: {success_count}")
print(f"  ✗ Failed Reports: {failed_count}")
print(f"  📊 Total: {total}")
print(f"  📁 Database File: health_reports.db")

# Show how to access via Admin Dashboard
print("\n" + "=" * 80)
print("🌐 HOW TO VIEW REPORTS:")
print("=" * 80)
print(f"  1. Admin Dashboard: http://localhost:10005/admin")
print(f"  2. API Endpoint: http://localhost:10005/api/admin/reports")
print(f"  3. Database File: health_reports.db (use SQLite browser)")
print(f"  4. Download PDFs: http://localhost:10005/report/{{id}}/download")

# Show sample report details
print("\n" + "=" * 80)
print("📋 SAMPLE REPORT DETAILS (Latest 3):")
print("=" * 80)

cursor.execute('''
    SELECT id, filename, full_results 
    FROM reports 
    WHERE full_results IS NOT NULL
    ORDER BY id DESC 
    LIMIT 3
''')

for row in cursor.fetchall():
    report_id, filename, full_results = row
    data = json.loads(full_results)
    
    print(f"\n  Report ID: {report_id}")
    print(f"  Filename: {filename}")
    print(f"  Parameters: {', '.join(list(data.get('extracted_parameters', {}).keys())[:5])}")
    print(f"  Risk Level: {data.get('overall_risk', 'N/A')}")
    print(f"  Recommendations: {len(data.get('recommendations', []))}")
    print(f"  Prescriptions: {len(data.get('prescriptions', []))}")
    print(f"  Download: http://localhost:10005/report/{report_id}/download")
    print("  " + "-" * 76)

conn.close()

print("\n" + "=" * 80)
print("✅ All reports are saved and accessible!")
print("=" * 80 + "\n")
