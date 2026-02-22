"""
Quick evaluation of improved extraction on key reports
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core_phase1.ocr.pdf_ocr import extract_text_from_pdf
from core_phase1.ocr.image_ocr import extract_text_from_image
from core_phase1.extraction.comprehensive_extractor import extract_parameters_comprehensive

def quick_evaluation():
    """Quick evaluation on all reports without classification."""
    
    test_dir = Path(r"C:\Users\mi\Downloads\infosys project\data\test_reports")
    
    # Get all test files
    pdf_files = sorted(test_dir.glob("*.pdf"))
    png_files = sorted(test_dir.glob("*.png"))
    all_files = pdf_files + png_files
    
    print("=" * 80)
    print("IMPROVED EXTRACTION EVALUATION")
    print("=" * 80)
    print(f"Total files: {len(all_files)} ({len(pdf_files)} PDFs, {len(png_files)} PNGs)\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "dataset": {
            "total_files": len(all_files),
            "pdf_files": len(pdf_files),
            "png_files": len(png_files)
        },
        "detailed_results": {}
    }
    
    success_count = 0
    ocr_success = 0
    total_parameters = 0
    
    for filepath in all_files:
        filename = filepath.name
        
        try:
            # Extract OCR text
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(str(filepath))
                file_format = "PDF"
            else:
                text = extract_text_from_image(str(filepath))
                file_format = "IMAGE"
            
            if len(text) == 0:
                results["detailed_results"][filename] = {
                    "status": "ocr_failed",
                    "format": "UNKNOWN",
                    "text_length": 0,
                    "parameters_found": 0
                }
                print(f"❌ {filename:30} - OCR failed")
                continue
            
            ocr_success += 1
            
            # Extract parameters
            extracted = extract_parameters_comprehensive(text)
            
            if not extracted:
                results["detailed_results"][filename] = {
                    "status": "no_parameters",
                    "format": file_format,
                    "text_length": len(text),
                    "parameters_found": 0
                }
                print(f"⚠️  {filename:30} - No parameters (text: {len(text)} chars)")
                continue
            
            results["detailed_results"][filename] = {
                "status": "success",
                "format": file_format,
                "text_length": len(text),
                "parameters_found": len(extracted),
                "parameters": list(extracted.keys())
            }
            
            success_count += 1
            total_parameters += len(extracted)
            
            print(f"✅ {filename:30} - {len(extracted):2} parameters")
            
        except Exception as e:
            results["detailed_results"][filename] = {
                "status": "error",
                "error": str(e),
                "format": "UNKNOWN",
                "text_length": 0,
                "parameters_found": 0
            }
            print(f"❌ {filename:30} - Error: {e}")
    
    # Calculate metrics
    ocr_success_rate = (ocr_success / len(all_files)) * 100
    extraction_success_rate = (success_count / len(all_files)) * 100
    workflow_success_rate = ocr_success_rate  # OCR is the critical step
    avg_parameters = total_parameters / success_count if success_count > 0 else 0
    
    results["metrics"] = {
        "ocr_success_rate": ocr_success_rate,
        "extraction_success_rate": extraction_success_rate,
        "workflow_success_rate": workflow_success_rate,
        "total_parameters_extracted": total_parameters,
        "avg_parameters_per_file": avg_parameters,
        "milestone_1_passed": extraction_success_rate >= 95.0
    }
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed:           {len(all_files)}")
    print(f"OCR successful:            {ocr_success} ({ocr_success_rate:.1f}%)")
    print(f"Parameters extracted:      {success_count} ({extraction_success_rate:.1f}%)")
    print(f"Total parameters:          {total_parameters}")
    print(f"Avg parameters per file:   {avg_parameters:.1f}")
    print(f"\n{'='*80}")
    print(f"Milestone 1 (>95% extraction): {'✅ PASSED' if results['metrics']['milestone_1_passed'] else '❌ FAILED'}")
    print(f"{'='*80}")
    
    # Compare with previous results
    try:
        with open('comprehensive_evaluation_20260218_150728.json', 'r') as f:
            old_results = json.load(f)
            old_rate = old_results['metrics']['extraction_success_rate']
            improvement = extraction_success_rate - old_rate
            print(f"\nIMPROVEMENT:")
            print(f"  Previous extraction rate: {old_rate:.1f}%")
            print(f"  New extraction rate:      {extraction_success_rate:.1f}%")
            print(f"  Improvement:              {improvement:+.1f}%")
    except:
        pass
    
    # Save results
    output_file = f"improved_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    quick_evaluation()
