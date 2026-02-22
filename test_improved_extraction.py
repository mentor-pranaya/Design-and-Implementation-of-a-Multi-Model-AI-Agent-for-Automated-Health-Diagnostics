"""
Test improved extraction on all test reports
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core_phase1.ocr.pdf_ocr import extract_text_from_pdf
from core_phase1.ocr.image_ocr import extract_text_from_image
from core_phase1.extraction.comprehensive_extractor import extract_parameters_comprehensive
from core_phase3.knowledge_base.unified_reference_manager import UnifiedReferenceManager

def test_all_reports():
    """Test improved extraction on all reports."""
    
    test_dir = Path(r"C:\Users\mi\Downloads\infosys project\data\test_reports")
    
    # Get all test files
    pdf_files = sorted(test_dir.glob("*.pdf"))
    png_files = sorted(test_dir.glob("*.png"))
    all_files = pdf_files + png_files
    
    print("=" * 80)
    print("TESTING IMPROVED EXTRACTION ON ALL REPORTS")
    print("=" * 80)
    print(f"Total files: {len(all_files)} ({len(pdf_files)} PDFs, {len(png_files)} PNGs)")
    
    # Initialize reference manager for classification
    ref_manager = UnifiedReferenceManager()
    
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
    total_parameters = 0
    
    for filepath in all_files:
        filename = filepath.name
        print(f"\n{'='*80}")
        print(f"Processing: {filename}")
        print(f"{'='*80}")
        
        try:
            # Extract OCR text
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(str(filepath))
                file_format = "PDF"
            else:
                text = extract_text_from_image(str(filepath))
                file_format = "IMAGE"
            
            print(f"  OCR text length: {len(text)} characters")
            
            if len(text) == 0:
                results["detailed_results"][filename] = {
                    "status": "ocr_failed",
                    "format": "UNKNOWN",
                    "text_length": 0,
                    "parameters_found": 0,
                    "parameters": {}
                }
                print("  ❌ OCR failed (no text extracted)")
                continue
            
            # Extract parameters
            extracted = extract_parameters_comprehensive(text)
            
            if not extracted:
                results["detailed_results"][filename] = {
                    "status": "no_parameters",
                    "format": file_format,
                    "text_length": len(text),
                    "parameters_found": 0,
                    "parameters": {}
                }
                print(f"  ⚠️  No parameters extracted")
                continue
            
            # Classify parameters
            classified_params = {}
            for param_name, param_data in extracted.items():
                try:
                    # Get classification
                    evaluation = ref_manager.evaluate_value(
                        param_name,
                        param_data["value"],
                        sex="male"  # Default for testing
                    )
                    
                    classified_params[param_name] = {
                        "value": param_data["value"],
                        "unit": param_data["unit"],
                        "raw_match": param_data["raw_match"],
                        "classification": evaluation.get("classification", "unknown")
                    }
                except Exception as e:
                    # If classification fails, still include the parameter
                    classified_params[param_name] = {
                        "value": param_data["value"],
                        "unit": param_data["unit"],
                        "raw_match": param_data["raw_match"],
                        "classification": "unknown"
                    }
            
            results["detailed_results"][filename] = {
                "status": "success",
                "format": file_format,
                "text_length": len(text),
                "parameters_found": len(classified_params),
                "parameters": classified_params
            }
            
            success_count += 1
            total_parameters += len(classified_params)
            
            print(f"  ✅ Extracted {len(classified_params)} parameters:")
            for param, data in classified_params.items():
                print(f"     {param:20} = {data['value']:8.2f} {data['unit']:10} [{data['classification']}]")
            
        except Exception as e:
            results["detailed_results"][filename] = {
                "status": "error",
                "error": str(e),
                "format": "UNKNOWN",
                "text_length": 0,
                "parameters_found": 0,
                "parameters": {}
            }
            print(f"  ❌ Error: {e}")
    
    # Calculate metrics
    extraction_success_rate = (success_count / len(all_files)) * 100
    avg_parameters = total_parameters / success_count if success_count > 0 else 0
    
    results["metrics"] = {
        "extraction_success_rate": extraction_success_rate,
        "total_parameters_extracted": total_parameters,
        "avg_parameters_per_file": avg_parameters,
        "milestone_1_passed": extraction_success_rate >= 95.0
    }
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed: {len(all_files)}")
    print(f"Successful extractions: {success_count}")
    print(f"Extraction success rate: {extraction_success_rate:.2f}%")
    print(f"Total parameters extracted: {total_parameters}")
    print(f"Average parameters per file: {avg_parameters:.2f}")
    print(f"\nMilestone 1 (>95% extraction): {'✅ PASSED' if results['metrics']['milestone_1_passed'] else '❌ FAILED'}")
    
    # Save results
    output_file = f"improved_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    test_all_reports()
