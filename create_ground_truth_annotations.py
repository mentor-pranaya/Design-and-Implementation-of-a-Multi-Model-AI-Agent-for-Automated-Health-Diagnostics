"""
Ground Truth Annotation Generator
Creates annotation templates for all test reports
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core_phase1.ocr.pdf_ocr import extract_text_from_pdf
from core_phase1.ocr.image_ocr import extract_text_from_image
from core_phase1.extraction.comprehensive_extractor import extract_parameters_comprehensive

def create_ground_truth_template(filepath):
    """Create ground truth annotation template for a report."""
    
    filename = filepath.name
    
    # Extract text
    if filepath.suffix == '.pdf':
        text = extract_text_from_pdf(str(filepath))
    else:
        text = extract_text_from_image(str(filepath))
    
    if len(text) == 0:
        return None
    
    # Extract parameters
    extracted = extract_parameters_comprehensive(text)
    
    if not extracted:
        return None
    
    # Create template
    template = {
        "filename": filename,
        "timestamp": datetime.now().isoformat(),
        "parameters": {}
    }
    
    for param_name, param_data in extracted.items():
        template["parameters"][param_name] = {
            "extracted_value": param_data["value"],
            "extracted_unit": param_data["unit"],
            "correct_value": param_data["value"],  # USER SHOULD VERIFY
            "correct_unit": param_data["unit"],     # USER SHOULD VERIFY
            "expected_classification": "unknown",    # USER SHOULD FILL
            "notes": ""                              # USER CAN ADD NOTES
        }
    
    return template

def generate_all_annotations():
    """Generate ground truth annotations for all reports."""
    
    test_dir = Path(r"C:\Users\mi\Downloads\infosys project\data\test_reports")
    output_dir = Path("evaluation/test_dataset/ground_truth")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_files = sorted(list(test_dir.glob("*.pdf")) + list(test_dir.glob("*.png")))
    
    print("=" * 80)
    print("GROUND TRUTH ANNOTATION GENERATOR")
    print("=" * 80)
    print(f"Total files: {len(all_files)}\n")
    
    generated = 0
    skipped = 0
    
    for filepath in all_files:
        filename = filepath.name
        print(f"Processing: {filename}")
        
        template = create_ground_truth_template(filepath)
        
        if template:
            # Save template
            output_file = output_dir / f"{filepath.stem}_ground_truth.json"
            with open(output_file, 'w') as f:
                json.dump(template, f, indent=2)
            
            print(f"  ✅ Created: {output_file.name}")
            print(f"  Parameters: {len(template['parameters'])}")
            generated += 1
        else:
            print(f"  ⚠️  Skipped (no parameters)")
            skipped += 1
        
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Templates generated: {generated}")
    print(f"Files skipped: {skipped}")
    print(f"\nOutput directory: {output_dir}")
    print("\n📝 NEXT STEPS:")
    print("1. Review each JSON file in evaluation/test_dataset/ground_truth/")
    print("2. Verify extracted values are correct")
    print("3. Fill in 'expected_classification' (normal/low/high)")
    print("4. Add any notes if needed")
    print("5. Run validation script to calculate accuracy")

if __name__ == "__main__":
    generate_all_annotations()
