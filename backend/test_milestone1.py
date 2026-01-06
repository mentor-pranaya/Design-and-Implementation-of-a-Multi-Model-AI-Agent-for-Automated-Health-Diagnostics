"""
Test script for Milestone 1
Tests the complete pipeline with sample reports
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.orchestrator import processing_pipeline

async def test_pipeline():
    """Test the processing pipeline with sample reports"""
    
    print("=" * 80)
    print("MILESTONE 1 TESTING: Data Ingestion & Parameter Interpretation")
    print("=" * 80)
    print()
    
    # Test files
    test_files = [
        "../data/sample_reports/sample_blood_report_1.json",
        "../data/sample_reports/sample_blood_report_2.json"
    ]
    
    for test_file in test_files:
        file_path = Path(test_file)
        
        if not file_path.exists():
            print(f"❌ Test file not found: {test_file}")
            continue
        
        print(f"\n{'='*80}")
        print(f"Testing: {file_path.name}")
        print(f"{'='*80}\n")
        
        # Test with user context
        user_context = {
            "age": 45,
            "gender": "male"
        }
        
        if "report_2" in test_file:
            user_context = {"age": 32, "gender": "female"}
        
        # Process report
        result = await processing_pipeline.process_report(str(file_path), user_context)
        
        # Display results
        print(f"Status: {result['status']}")
        print(f"Processing Time: {result.get('processing_time_seconds', 0):.2f}s")
        print()
        
        if result['status'] == 'completed':
            # Extraction
            print("📥 EXTRACTION:")
            print(f"  - Method: {result['pipeline_stages']['extraction']['method']}")
            print(f"  - Extracted: {result['pipeline_stages']['extraction']['total_extracted']} parameters")
            print()
            
            # Validation
            print("✅ VALIDATION:")
            print(f"  - Validated: {result['pipeline_stages']['validation']['total_validated']} parameters")
            print(f"  - Invalid: {result['pipeline_stages']['validation']['total_invalid']} parameters")
            if result['pipeline_stages']['validation']['issues']:
                print(f"  - Issues:")
                for issue in result['pipeline_stages']['validation']['issues']:
                    print(f"    • {issue['parameter']}: {issue['issue']}")
            print()
            
            # Interpretation Summary
            summary = result['summary']
            print("🔍 INTERPRETATION SUMMARY:")
            print(f"  - Total Parameters: {summary['total_parameters']}")
            print(f"  - Critical: {summary['critical_count']}")
            print(f"  - Abnormal: {summary['abnormal_count']}")
            print(f"  - Normal: {summary['normal_count']}")
            print()
            
            # Critical Findings
            if result['critical_findings']:
                print("🚨 CRITICAL FINDINGS:")
                for finding in result['critical_findings']:
                    print(f"  • {finding['parameter']}: {finding['value']} {finding['unit']}")
                    print(f"    Status: {finding['status'].upper()}")
                    print(f"    {finding['clinical_significance']}")
                print()
            
            # Abnormal Findings
            if result['abnormal_findings']:
                print("⚠️  ABNORMAL FINDINGS:")
                for finding in result['abnormal_findings']:
                    print(f"  • {finding['parameter']}: {finding['value']} {finding['unit']}")
                    print(f"    Status: {finding['status']}")
                    print(f"    Reference: {finding['reference_range']['min']}-{finding['reference_range']['max']} {finding['unit']}")
                    print(f"    {finding['clinical_significance']}")
                print()
            
            # Confidence Scores
            print("📊 CONFIDENCE SCORES:")
            print(f"  - Extraction: {result['confidence_scores']['extraction']:.2%}")
            print(f"  - Validation: {result['confidence_scores']['validation']:.2%}")
            print(f"  - Interpretation: {result['confidence_scores']['interpretation']:.2%}")
            print()
            
        else:
            print(f"❌ Error: {result.get('error')}")
            print()
    
    print("=" * 80)
    print("MILESTONE 1 TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_pipeline())
