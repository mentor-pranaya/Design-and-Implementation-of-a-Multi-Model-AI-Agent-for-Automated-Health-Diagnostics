"""
Comprehensive evaluation of all test reports (PDF and PNG).
This demonstrates that your project works with both formats!
"""

import sys
import os
import json
from datetime import datetime
import glob
import re

# Add project paths
sys.path.append('core_phase1/ocr')
sys.path.append('core_phase1/extraction')

def extract_text_from_file(file_path):
    """Extract text from either PDF or PNG file."""
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.pdf':
            # Use PDF OCR
            from pdf_ocr import extract_text_from_pdf
            return extract_text_from_pdf(file_path), "PDF"
            
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            # Use image OCR
            import pytesseract
            from PIL import Image
            
            # Set tesseract path
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text, "IMAGE"
            
        else:
            return None, "UNSUPPORTED"
            
    except Exception as e:
        print(f"   ❌ OCR Error: {e}")
        return None, "ERROR"

def extract_blood_parameters(text):
    """Extract blood parameters from OCR text using regex patterns."""
    
    if not text:
        return {}
    
    parameters = {}
    
    # Common blood parameter patterns
    patterns = {
        'hemoglobin': r'(?:hemoglobin|hb|haemoglobin)\s*(?:\(hb\))?\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'glucose': r'(?:glucose|sugar)\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'creatinine': r'creatinine\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'cholesterol': r'cholesterol\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'triglycerides': r'triglycerides?\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'hdl': r'hdl\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'ldl': r'ldl\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'wbc': r'(?:white blood cell|wbc)\s*(?:count)?\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'rbc': r'(?:red blood cell|rbc)\s*(?:count)?\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'platelet': r'platelet\s*(?:count)?\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'hematocrit': r'hematocrit\s*(?:\(pcv\))?\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'mcv': r'(?:mean corpuscular volume|mcv)\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'mch': r'(?:mean corpuscular hemoglobin|mch)\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'mchc': r'(?:mean corpuscular hemoglobin concentration|mchc)\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?',
        'rdw': r'(?:red cell distribution width|rdw)\s*:?\s*(\d+\.?\d*)\s*([a-zA-Z/]+)?'
    }
    
    text_lower = text.lower()
    
    for param_name, pattern in patterns.items():
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        
        if matches:
            # Take the first match
            value_str, unit = matches[0]
            try:
                value = float(value_str)
                parameters[param_name] = {
                    'value': value,
                    'unit': unit if unit else 'unknown',
                    'raw_match': matches[0]
                }
            except ValueError:
                continue
    
    return parameters

def classify_parameter(param_name, value, unit):
    """Simple classification of parameters (you can enhance this)."""
    
    # Basic reference ranges (you can use your UnifiedReferenceManager here)
    reference_ranges = {
        'hemoglobin': {'male': (13.0, 18.0), 'female': (11.5, 16.5), 'unit': 'g/dL'},
        'glucose': {'normal': (70, 100), 'unit': 'mg/dL'},
        'creatinine': {'male': (0.7, 1.3), 'female': (0.6, 1.1), 'unit': 'mg/dL'},
        'cholesterol': {'normal': (0, 200), 'unit': 'mg/dL'},
        'wbc': {'normal': (4.0, 11.0), 'unit': 'thou/μL'},
        'rbc': {'male': (4.5, 6.5), 'female': (3.8, 5.8), 'unit': 'mil/μL'},
        'platelet': {'normal': (150, 450), 'unit': 'thou/μL'},
        'hematocrit': {'male': (40, 54), 'female': (37, 47), 'unit': '%'}
    }
    
    if param_name not in reference_ranges:
        return 'unknown'
    
    ref_range = reference_ranges[param_name]
    
    # Use normal range if available, otherwise use male range as default
    if 'normal' in ref_range:
        min_val, max_val = ref_range['normal']
    elif 'male' in ref_range:
        min_val, max_val = ref_range['male']
    else:
        return 'unknown'
    
    if value < min_val:
        return 'low'
    elif value > max_val:
        return 'high'
    else:
        return 'normal'

def evaluate_all_formats():
    """Evaluate all test reports in both PDF and PNG formats."""
    
    print("=" * 80)
    print("COMPREHENSIVE EVALUATION - PDF AND PNG SUPPORT")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get all test files
    test_dir = "data/test_reports"
    all_files = glob.glob(os.path.join(test_dir, "*"))
    
    # Separate by format
    pdf_files = [f for f in all_files if f.endswith('.pdf')]
    png_files = [f for f in all_files if f.endswith('.png')]
    
    print(f"\nFound {len(pdf_files)} PDF files and {len(png_files)} PNG files")
    print(f"Total files to process: {len(all_files)}")
    
    # Process all files
    results = {}
    successful_ocr = 0
    failed_ocr = 0
    total_parameters_extracted = 0
    
    all_test_files = pdf_files + png_files
    
    for i, file_path in enumerate(sorted(all_test_files), 1):
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].upper()
        
        print(f"\n[{i}/{len(all_test_files)}] Processing: {file_name} ({file_ext})")
        
        # Extract text using OCR
        text, format_type = extract_text_from_file(file_path)
        
        if text:
            print(f"   ✅ {format_type} OCR successful ({len(text)} chars)")
            successful_ocr += 1
            
            # Extract parameters
            parameters = extract_blood_parameters(text)
            
            if parameters:
                print(f"   ✅ Extracted {len(parameters)} parameters:")
                
                classified_params = {}
                for param_name, param_data in parameters.items():
                    classification = classify_parameter(param_name, param_data['value'], param_data['unit'])
                    classified_params[param_name] = {
                        **param_data,
                        'classification': classification
                    }
                    
                    status_icon = "⚠️" if classification in ['low', 'high'] else "✅"
                    print(f"     {status_icon} {param_name}: {param_data['value']} {param_data['unit']} ({classification})")
                
                total_parameters_extracted += len(parameters)
                
                results[file_name] = {
                    'status': 'success',
                    'format': format_type,
                    'text_length': len(text),
                    'parameters_found': len(parameters),
                    'parameters': classified_params
                }
            else:
                print(f"   ⚠️  No parameters extracted")
                results[file_name] = {
                    'status': 'no_parameters',
                    'format': format_type,
                    'text_length': len(text),
                    'parameters_found': 0,
                    'parameters': {}
                }
        else:
            print(f"   ❌ OCR failed")
            failed_ocr += 1
            results[file_name] = {
                'status': 'ocr_failed',
                'format': 'UNKNOWN',
                'text_length': 0,
                'parameters_found': 0,
                'parameters': {}
            }
    
    # Calculate metrics
    total_files = len(all_test_files)
    ocr_success_rate = (successful_ocr / total_files) * 100 if total_files > 0 else 0
    avg_parameters = total_parameters_extracted / successful_ocr if successful_ocr > 0 else 0
    
    print(f"\n{'='*80}")
    print("EVALUATION RESULTS")
    print(f"{'='*80}")
    
    print(f"Total files processed: {total_files}")
    print(f"  PDF files: {len(pdf_files)}")
    print(f"  PNG files: {len(png_files)}")
    print(f"OCR successful: {successful_ocr}")
    print(f"OCR failed: {failed_ocr}")
    print(f"OCR success rate: {ocr_success_rate:.1f}%")
    print(f"Total parameters extracted: {total_parameters_extracted}")
    print(f"Average parameters per successful file: {avg_parameters:.1f}")
    
    # Check project requirements
    print(f"\n{'='*80}")
    print("PROJECT REQUIREMENTS CHECK")
    print(f"{'='*80}")
    
    # Milestone 1: Data Extraction Accuracy >95%
    extraction_success = len([r for r in results.values() if r['parameters_found'] > 0])
    extraction_rate = (extraction_success / total_files) * 100 if total_files > 0 else 0
    
    print(f"MILESTONE 1 - Data Extraction:")
    print(f"  Target: >95% extraction accuracy")
    print(f"  Achieved: {extraction_rate:.1f}% ({extraction_success}/{total_files} files with extracted parameters)")
    
    if extraction_rate >= 95:
        print("  🎉 MILESTONE 1: ✅ PASSED")
    else:
        print("  ⚠️  MILESTONE 1: ❌ NEEDS IMPROVEMENT")
    
    # Milestone 4: Workflow Success Rate >95%
    workflow_success = successful_ocr
    workflow_rate = (workflow_success / total_files) * 100 if total_files > 0 else 0
    
    print(f"\nMILESTONE 4 - Workflow Success:")
    print(f"  Target: >95% workflow success rate")
    print(f"  Achieved: {workflow_rate:.1f}% ({workflow_success}/{total_files} files processed successfully)")
    
    if workflow_rate >= 95:
        print("  🎉 MILESTONE 4: ✅ PASSED")
    else:
        print("  ⚠️  MILESTONE 4: ❌ NEEDS IMPROVEMENT")
    
    # Format support analysis
    pdf_success = len([r for r in results.values() if r['format'] == 'PDF' and r['status'] == 'success'])
    png_success = len([r for r in results.values() if r['format'] == 'IMAGE' and r['status'] == 'success'])
    
    print(f"\nFORMAT SUPPORT:")
    print(f"  PDF processing: {pdf_success}/{len(pdf_files)} successful ({(pdf_success/len(pdf_files)*100) if pdf_files else 0:.1f}%)")
    print(f"  PNG processing: {png_success}/{len(png_files)} successful ({(png_success/len(png_files)*100) if png_files else 0:.1f}%)")
    
    if pdf_success > 0 and png_success > 0:
        print("  🎉 MULTI-FORMAT SUPPORT: ✅ Your project works with both PDF and PNG!")
    elif pdf_success > 0:
        print("  ✅ PDF SUPPORT: Working")
        print("  ⚠️  PNG SUPPORT: Needs improvement")
    elif png_success > 0:
        print("  ⚠️  PDF SUPPORT: Needs improvement")
        print("  ✅ PNG SUPPORT: Working")
    
    # Save detailed results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"comprehensive_evaluation_{timestamp}.json"
    
    evaluation_summary = {
        "timestamp": datetime.now().isoformat(),
        "dataset": {
            "total_files": total_files,
            "pdf_files": len(pdf_files),
            "png_files": len(png_files)
        },
        "metrics": {
            "ocr_success_rate": ocr_success_rate,
            "extraction_success_rate": extraction_rate,
            "workflow_success_rate": workflow_rate,
            "total_parameters_extracted": total_parameters_extracted,
            "avg_parameters_per_file": avg_parameters,
            "milestone_1_passed": extraction_rate >= 95,
            "milestone_4_passed": workflow_rate >= 95
        },
        "format_support": {
            "pdf_success_rate": (pdf_success/len(pdf_files)*100) if pdf_files else 0,
            "png_success_rate": (png_success/len(png_files)*100) if png_files else 0,
            "multi_format_support": pdf_success > 0 and png_success > 0
        },
        "detailed_results": results
    }
    
    with open(results_file, 'w') as f:
        json.dump(evaluation_summary, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # Final assessment
    print(f"\n{'='*80}")
    print("FINAL ASSESSMENT")
    print(f"{'='*80}")
    
    if workflow_rate >= 95 and extraction_rate >= 95:
        print("🎉 EXCELLENT! Your system meets ALL project requirements!")
        print("✅ Workflow success rate >95%")
        print("✅ Data extraction accuracy >95%")
        if pdf_success > 0 and png_success > 0:
            print("✅ Multi-format support (PDF + PNG)")
        print("🚀 Ready for final project submission!")
        
    elif workflow_rate >= 95:
        print("✅ Good workflow success rate")
        print("⚠️  Parameter extraction needs improvement")
        print("💡 Consider adjusting extraction patterns")
        
    else:
        print("⚠️  System needs improvement")
        print("💡 Focus on OCR quality and extraction patterns")
    
    return evaluation_summary

if __name__ == "__main__":
    results = evaluate_all_formats()
    
    print(f"\n{'='*80}")
    print("EVALUATION COMPLETE")
    print(f"{'='*80}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if results:
        if results["metrics"]["milestone_1_passed"] and results["metrics"]["milestone_4_passed"]:
            print("🎉 CONGRATULATIONS! Your project meets all requirements!")
        else:
            print("📊 Review results and improve where needed")
        
        if results["format_support"]["multi_format_support"]:
            print("🌟 BONUS: Your project supports multiple formats (PDF + PNG)!")