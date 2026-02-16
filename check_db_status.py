import sqlite3
import json
from datetime import datetime

print("=" * 60)
print("DATABASE STATUS CHECK - INBLOODO AI")
print("=" * 60)

try:
    # Connect to database
    conn = sqlite3.connect('health_reports.db')
    cursor = conn.cursor()
    
    # 1. Total Reports
    cursor.execute('SELECT COUNT(*) FROM reports')
    total = cursor.fetchone()[0]
    print(f"\n✓ Total Reports in Database: {total}")
    
    # 2. Recent Reports (Last 10)
    cursor.execute('''
        SELECT id, filename, created_at, description 
        FROM reports 
        ORDER BY id DESC 
        LIMIT 10
    ''')
    
    print(f"\n{'='*60}")
    print("RECENT REPORTS (Last 10):")
    print(f"{'='*60}")
    print(f"{'ID':<6} {'Filename':<25} {'Created':<20} {'Status':<10}")
    print("-" * 60)
    
    for row in cursor.fetchall():
        report_id, filename, created_at, description = row
        status = "✓ Success" if description and "failed" not in description.lower() else "✗ Failed"
        created_str = created_at[:19] if created_at else "N/A"
        filename_short = (filename[:22] + "...") if filename and len(filename) > 25 else (filename or "N/A")
        print(f"{report_id:<6} {filename_short:<25} {created_str:<20} {status:<10}")
    
    # 3. Reports with Full Results
    cursor.execute('SELECT COUNT(*) FROM reports WHERE full_results IS NOT NULL')
    with_full = cursor.fetchone()[0]
    print(f"\n✓ Reports with Full Analysis Data: {with_full}/{total}")
    
    # 4. Check Latest Report Details
    cursor.execute('''
        SELECT id, filename, full_results 
        FROM reports 
        ORDER BY id DESC 
        LIMIT 1
    ''')
    
    latest = cursor.fetchone()
    if latest:
        report_id, filename, full_results = latest
        print(f"\n{'='*60}")
        print(f"LATEST REPORT DETAILS (ID: {report_id}):")
        print(f"{'='*60}")
        print(f"Filename: {filename}")
        
        if full_results:
            data = json.loads(full_results)
            print(f"Status: {data.get('status', 'unknown')}")
            print(f"Parameters: {len(data.get('extracted_parameters', {}))}")
            print(f"Risks: {len(data.get('risks', []))}")
            print(f"Recommendations: {len(data.get('recommendations', []))}")
            print(f"Prescriptions: {len(data.get('prescriptions', []))}")
            print(f"Overall Risk: {data.get('overall_risk', 'N/A')}")
        else:
            print("⚠ No full_results data available")
    
    # 5. Database Schema Check
    cursor.execute("PRAGMA table_info(reports)")
    columns = cursor.fetchall()
    print(f"\n{'='*60}")
    print("DATABASE SCHEMA:")
    print(f"{'='*60}")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print("✓ DATABASE IS WORKING CORRECTLY")
    print(f"{'='*60}\n")
    
except Exception as e:
    print(f"\n✗ DATABASE ERROR: {str(e)}\n")
    import traceback
    traceback.print_exc()
