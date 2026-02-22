"""
Evaluate all test reports using the working orchestrator.
"""

import sys
import os
import json
from datetime import datetime
import glob

# Add project paths
sys.path.append('core_phase3')

def evaluate_all_reports():
    """Evaluate all test reports."""
    
    print("=" * 80)
    print("EVALUATING ALL TEST REPORTS")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Import orchestrator
    try:
        from orchestrator import MultiModelOrchestrator
        print("✅ Successfully imported MultiModelOrchestrator")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Initialize orchestrator
    try:
        orchestrator = MultiModelOrchestrator(verbose=False)  # Less verbose for batch processing
        print("✅ Successfully initialized orchestrator")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        return
    
    # Get all PDF test reports (PNG processing not implemented yet)
    test_dir = "data/test_reports"
    pdf_reports = glob.glob(os.path.join(test_dir, "*.pdf"))
    png_reports = glob.glob(os.path.join(test_dir, "*.png"))
    
    print(f"\nFound {len(pdf_reports)} PDF reports and {len(png_reports)} PNG reports")
    print("Processing PDF reports (PNG processing not yet implemented)")
    
    # Process all PDF reports
    results = {}
    successful = 0
    failed = 0
    
    for i, report_path in enumerate(sorted(pdf_reports), 1):
        report_name = os.path.basename(report_path)
        print(f"\n[{i}/{len(pdf_reports)}] Processing: {report_name}")
        
        try:
            result = orchestrator.process_blood_report(report_path)
            
            if result.get("status") == "success":
                successful += 1
                print(f"  ✅ SUCCESS")
                
                # Check if any parameters were extracted
                findings = result.get("report", {}).get("findings", {})
                abnormal_params = findings.get("abnormal_parameters", [])
                detected_patterns = findings.get("detected_patterns", [])
                
                print(f"    Abnormal parameters: {len(abnormal_params)}")
                print(f"    Detected patterns: {len(detected_patterns)}")
                
            else:
                failed += 1
                print(f"  ❌ FAILED")
            
            results[report_name] = result
            
        except Exception as e:
            failed += 1
            print(f"  ❌ ERROR: {str(e)}")
            results[report_name] = {"status": "error", "error": str(e)}
    
    # Calculate metrics
    total_reports = len(pdf_reports)
    success_rate = (successful / total_reports) * 100 if total_reports > 0 else 0
    
    print(f"\n{'='*80}")
    print("EVALUATION RESULTS")
    print(f"{'='*80}")
    print(f"Total PDF reports processed: {total_reports}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {success_rate:.1f}%")
    
    # Check against project requirements
    print(f"\n{'='*80}")
    print("PROJECT REQUIREMENTS CHECK")
    print(f"{'='*80}")
    
    # Milestone 4: End-to-end workflow success rate of >95%
    if success_rate >= 95:
        print("🎉 MILESTONE 4: ✅ PASSED")
        print(f"   Target: >95% workflow success rate")
        print(f"   Achieved: {success_rate:.1f}%")
    else:
        print("⚠️  MILESTONE 4: ❌ NEEDS IMPROVEMENT")
        print(f"   Target: >95% workflow success rate")
        print(f"   Achieved: {success_rate:.1f}%")
        print(f"   Gap: {95 - success_rate:.1f}%")
    
    # Analyze successful results
    successful_results = {k: v for k, v in results.items() if v.get("status") == "success"}
    
    if successful_results:
        print(f"\n{'='*80}")
        print(f"ANALYSIS OF SUCCESSFUL RESULTS ({len(successful_results)} reports)")
        print(f"{'='*80}")
        
        total_abnormal = 0
        total_patterns = 0
        
        for report_name, result in successful_results.items():
            findings = result.get("report", {}).get("findings", {})
            abnormal_params = findings.get("abnormal_parameters", [])
            detected_patterns = findings.get("detected_patterns", [])
            
            total_abnormal += len(abnormal_params)
            total_patterns += len(detected_patterns)
        
        avg_abnormal = total_abnormal / len(successful_results)
        avg_patterns = total_patterns / len(successful_results)
        
        print(f"Average abnormal parameters per report: {avg_abnormal:.1f}")
        print(f"Average detected patterns per report: {avg_patterns:.1f}")
        
        if avg_abnormal == 0 and avg_patterns == 0:
            print("\n⚠️  WARNING: No abnormal parameters or patterns detected")
            print("   This might indicate:")
            print("   - OCR extraction issues")
            print("   - All reports contain normal values")
            print("   - Parameter extraction needs debugging")
    
    # Save detailed results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"evaluation_results_{timestamp}.json"
    
    evaluation_summary = {
        "timestamp": datetime.now().isoformat(),
        "dataset": {
            "total_files": len(pdf_reports) + len(png_reports),
            "pdf_reports": len(pdf_reports),
            "png_reports": len(png_reports),
            "processed": total_reports
        },
        "metrics": {
            "total_processed": total_reports,
            "successful": successful,
            "failed": failed,
            "success_rate_percent": success_rate,
            "milestone_4_target": 95.0,
            "milestone_4_passed": success_rate >= 95
        },
        "detailed_results": results
    }
    
    with open(results_file, 'w') as f:
        json.dump(evaluation_summary, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # Recommendations
    print(f"\n{'='*80}")
    print("RECOMMENDATIONS")
    print(f"{'='*80}")
    
    if success_rate >= 95:
        print("✅ Excellent! Your system meets Milestone 4 requirements")
        print("✅ Ready for final project submission")
        
        if avg_abnormal == 0 and avg_patterns == 0:
            print("⚠️  Consider investigating why no abnormalities were detected")
            print("   - Check if test reports contain abnormal values")
            print("   - Verify OCR extraction is working correctly")
            print("   - Test with reports known to have abnormal values")
    
    elif success_rate >= 80:
        print("⚠️  Good performance but needs improvement for Milestone 4")
        print("   - Review failed cases")
        print("   - Improve error handling")
        print("   - Test with simpler reports first")
    
    else:
        print("❌ Significant issues found")
        print("   - Review system architecture")
        print("   - Check OCR and extraction components")
        print("   - Test individual components separately")
    
    print(f"\nNext steps:")
    print("1. Review the detailed results JSON file")
    print("2. If success rate is good, investigate parameter extraction")
    print("3. Create ground truth annotations for manual verification")
    print("4. Calculate detailed accuracy metrics (extraction, classification)")
    
    return evaluation_summary

if __name__ == "__main__":
    results = evaluate_all_reports()
    
    print(f"\n{'='*80}")
    print("EVALUATION COMPLETE")
    print(f"{'='*80}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if results:
        success_rate = results["metrics"]["success_rate_percent"]
        if success_rate >= 95:
            print("🎉 CONGRATULATIONS! Your system meets project requirements!")
        else:
            print(f"📊 Current success rate: {success_rate:.1f}% (Target: 95%)")