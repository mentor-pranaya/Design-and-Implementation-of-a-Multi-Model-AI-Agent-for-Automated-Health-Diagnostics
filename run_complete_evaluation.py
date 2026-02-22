"""
Complete evaluation pipeline for all test reports.
This script will:
1. Process all test reports through the full pipeline
2. Extract data and generate results
3. Create evaluation metrics
4. Generate comprehensive report
"""

import os
import sys
import json
import traceback
from datetime import datetime
import glob

# Add project paths
sys.path.append('core_phase1')
sys.path.append('core_phase2')
sys.path.append('core_phase3')

# Import your pipeline components
try:
    from core_phase1.ocr.pdf_processor import PDFProcessor
    from core_phase1.extraction.parameter_extractor import ParameterExtractor
    from core_phase1.validation.validator import Validator
    from core_phase2.interpreter.model2_patterns import detect_all_patterns
    from core_phase3.orchestrator import MultiModelOrchestrator
    from core_phase3.knowledge_base.unified_reference_manager import UnifiedReferenceManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all modules are available")

def process_single_report(report_path, orchestrator):
    """Process a single blood report through the complete pipeline."""
    try:
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(report_path)}")
        print(f"{'='*60}")
        
        # Determine file type and process accordingly
        if report_path.endswith('.pdf'):
            # Use orchestrator for PDF processing
            result = orchestrator.process_blood_report(report_path)
        elif report_path.endswith('.png'):
            # For PNG files, you might need image OCR
            print("PNG processing - would need image OCR implementation")
            result = {"status": "skipped", "reason": "PNG processing not implemented yet"}
        else:
            result = {"status": "error", "reason": "Unsupported file format"}
        
        return result
        
    except Exception as e:
        print(f"Error processing {report_path}: {str(e)}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

def run_evaluation():
    """Run complete evaluation on all test reports."""
    
    print("=" * 80)
    print("COMPLETE EVALUATION PIPELINE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize orchestrator
    try:
        orchestrator = MultiModelOrchestrator()
        print("✅ MultiModelOrchestrator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        return
    
    # Get all test reports
    test_dir = "data/test_reports"
    pdf_reports = glob.glob(os.path.join(test_dir, "*.pdf"))
    png_reports = glob.glob(os.path.join(test_dir, "*.png"))
    
    print(f"\nFound {len(pdf_reports)} PDF reports and {len(png_reports)} PNG reports")
    
    # Process all reports
    results = {}
    successful_processes = 0
    failed_processes = 0
    
    # Process PDF reports first (these should work with your current pipeline)
    print(f"\n{'='*80}")
    print("PROCESSING PDF REPORTS")
    print(f"{'='*80}")
    
    for report_path in sorted(pdf_reports):
        report_name = os.path.basename(report_path)
        result = process_single_report(report_path, orchestrator)
        results[report_name] = result
        
        if result.get("status") == "success":
            successful_processes += 1
            print(f"✅ {report_name}: SUCCESS")
        else:
            failed_processes += 1
            print(f"❌ {report_name}: FAILED - {result.get('error', 'Unknown error')}")
    
    # Process PNG reports (note limitations)
    if png_reports:
        print(f"\n{'='*80}")
        print("PROCESSING PNG REPORTS (Limited Support)")
        print(f"{'='*80}")
        
        for report_path in sorted(png_reports):
            report_name = os.path.basename(report_path)
            result = process_single_report(report_path, orchestrator)
            results[report_name] = result
            
            if result.get("status") == "success":
                successful_processes += 1
                print(f"✅ {report_name}: SUCCESS")
            else:
                failed_processes += 1
                print(f"⚠️  {report_name}: SKIPPED - {result.get('reason', 'PNG processing not implemented')}")
    
    # Generate summary
    print(f"\n{'='*80}")
    print("EVALUATION SUMMARY")
    print(f"{'='*80}")
    
    total_reports = len(pdf_reports) + len(png_reports)
    success_rate = (successful_processes / total_reports) * 100 if total_reports > 0 else 0
    
    print(f"Total reports processed: {total_reports}")
    print(f"Successful: {successful_processes}")
    print(f"Failed/Skipped: {failed_processes}")
    print(f"Success rate: {success_rate:.1f}%")
    
    # Milestone 4 target: >95% workflow success rate
    if success_rate >= 95:
        print("🎉 SUCCESS: Meets Milestone 4 target (>95% workflow success rate)")
    else:
        print(f"⚠️  Below target: Need {95 - success_rate:.1f}% improvement for Milestone 4")
    
    # Save detailed results
    results_file = f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_reports": total_reports,
                "successful": successful_processes,
                "failed": failed_processes,
                "success_rate": success_rate
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # Generate recommendations
    print(f"\n{'='*80}")
    print("RECOMMENDATIONS")
    print(f"{'='*80}")
    
    if success_rate >= 95:
        print("✅ Your system meets the project requirements!")
        print("✅ Ready for final submission")
        print("✅ Consider running additional analysis on successful results")
    elif success_rate >= 80:
        print("⚠️  Good performance but needs improvement")
        print("⚠️  Review failed cases and fix common issues")
        print("⚠️  Consider adding error handling for edge cases")
    else:
        print("❌ Significant issues found")
        print("❌ Review system architecture and error handling")
        print("❌ Test with simpler reports first")
    
    print(f"\nNext steps:")
    print("1. Review detailed results in the JSON file")
    print("2. Analyze successful cases for patterns")
    print("3. Fix issues in failed cases")
    print("4. Create ground truth annotations for successful cases")
    print("5. Calculate detailed metrics (extraction accuracy, classification accuracy)")
    
    return results

def analyze_successful_results(results):
    """Analyze the successful results to extract insights."""
    successful_results = {k: v for k, v in results.items() if v.get("status") == "success"}
    
    if not successful_results:
        print("No successful results to analyze")
        return
    
    print(f"\n{'='*80}")
    print(f"ANALYSIS OF SUCCESSFUL RESULTS ({len(successful_results)} reports)")
    print(f"{'='*80}")
    
    # Analyze extracted parameters
    all_parameters = set()
    parameter_counts = {}
    
    for report_name, result in successful_results.items():
        if "extracted_data" in result:
            extracted = result["extracted_data"]
            for param in extracted.keys():
                all_parameters.add(param)
                parameter_counts[param] = parameter_counts.get(param, 0) + 1
    
    print(f"\nParameters found across all successful reports:")
    for param in sorted(all_parameters):
        count = parameter_counts[param]
        percentage = (count / len(successful_results)) * 100
        print(f"  {param}: {count}/{len(successful_results)} reports ({percentage:.1f}%)")
    
    # Common parameters (found in >50% of reports)
    common_params = [p for p, c in parameter_counts.items() if c > len(successful_results) * 0.5]
    print(f"\nCommon parameters (>50% of reports): {len(common_params)}")
    for param in sorted(common_params):
        print(f"  ✅ {param}")
    
    return successful_results

if __name__ == "__main__":
    # Run the complete evaluation
    results = run_evaluation()
    
    # Analyze successful results
    if results:
        analyze_successful_results(results)
    
    print(f"\n{'='*80}")
    print("EVALUATION COMPLETE")
    print(f"{'='*80}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")