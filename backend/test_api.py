"""
Test API endpoints with sample reports
"""

import asyncio
import httpx
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_upload_and_analyze():
    """Test uploading a report and retrieving analysis"""
    
    print("=" * 80)
    print("TESTING API ENDPOINTS")
    print("=" * 80)
    print()
    
    async with httpx.AsyncClient() as client:
        # Test 1: Upload JSON report
        test_file = Path("../data/sample_reports/sample_blood_report_1.json")
        
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return
        
        print(f"📤 Uploading: {test_file.name}")
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/json')}
            data = {'age': '45', 'gender': 'male'}
            
            response = await client.post(
                f"{BASE_URL}/reports/upload",
                files=files,
                data=data,
                timeout=30.0
            )
        
        if response.status_code == 200:
            result = response.json()
            report_id = result['report_id']
            print(f"✅ Upload successful!")
            print(f"   Report ID: {report_id}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            print()
            
            # Test 2: Get report analysis
            print(f"📥 Retrieving analysis for Report ID: {report_id}")
            response = await client.get(f"{BASE_URL}/reports/{report_id}")
            
            if response.status_code == 200:
                analysis = response.json()
                print(f"✅ Analysis retrieved!")
                print()
                print(f"Status: {analysis['status']}")
                print(f"Extraction Confidence: {analysis['extraction_confidence']:.2%}")
                print(f"Analysis Confidence: {analysis['analysis_confidence']:.2%}")
                print()
                
                if analysis['critical_findings']:
                    print("🚨 CRITICAL FINDINGS:")
                    for finding in analysis['critical_findings']:
                        print(f"  • {finding}")
                    print()
                
                if analysis['abnormal_findings']:
                    print("⚠️  ABNORMAL FINDINGS:")
                    for finding in analysis['abnormal_findings']:
                        print(f"  • {finding}")
                    print()
                
                print("📝 SUMMARY:")
                summary = analysis['summary']
                print(f"  Total Parameters: {summary['total_parameters']}")
                print(f"  Critical: {summary['critical_count']}")
                print(f"  Abnormal: {summary['abnormal_count']}")
                print(f"  Normal: {summary['normal_count']}")
                print()
            else:
                print(f"❌ Failed to retrieve analysis: {response.status_code}")
                print(response.text)
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
        
        # Test 3: List reports
        print("📋 Listing all reports")
        response = await client.get(f"{BASE_URL}/reports/?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total']} reports")
            for report in data['reports']:
                print(f"  • ID {report['id']}: {report['filename']} ({report['status']})")
        else:
            print(f"❌ Failed to list reports: {response.status_code}")
    
    print()
    print("=" * 80)
    print("API TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    print("\n⚠️  Make sure the FastAPI server is running on http://127.0.0.1:8000\n")
    print("Start it with: uvicorn app.main:app --reload\n")
    
    try:
        asyncio.run(test_upload_and_analyze())
    except httpx.ConnectError:
        print("❌ Could not connect to server. Make sure it's running!")
