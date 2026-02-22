"""
Analyze OCR text from failed extractions to identify missing patterns.
"""
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core_phase1.ocr.pdf_ocr import extract_text_from_pdf
from core_phase1.ocr.image_ocr import extract_text_from_image

def analyze_failed_files():
    """Analyze files that failed parameter extraction."""
    
    test_dir = Path(r"C:\Users\mi\Downloads\infosys project\data\test_reports")
    
    # Files that failed extraction
    failed_files = [
        "test report (11).pdf",
        "test report (12).pdf", 
        "test report (14).pdf",
        "test report (15).pdf",
        "test report (4).png",
        "test report (5).pdf",
        "test report (6).pdf",
        "test report (7).pdf"
    ]
    
    print("=" * 80)
    print("ANALYZING FAILED EXTRACTIONS")
    print("=" * 80)
    
    for filename in failed_files[:3]:  # Analyze first 3 files
        filepath = test_dir / filename
        
        if not filepath.exists():
            print(f"\n❌ File not found: {filename}")
            continue
            
        print(f"\n{'=' * 80}")
        print(f"FILE: {filename}")
        print(f"{'=' * 80}")
        
        # Extract text
        try:
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(str(filepath))
            else:
                text = extract_text_from_image(str(filepath))
                
            print(f"\nText length: {len(text)} characters")
            print(f"\nFirst 2000 characters:")
            print("-" * 80)
            print(text[:2000])
            print("-" * 80)
            
            # Look for common blood test parameter names
            common_params = [
                'hemoglobin', 'hb', 'hgb',
                'glucose', 'sugar', 'fbs', 'rbs',
                'creatinine', 'creat',
                'cholesterol', 'chol',
                'triglyceride', 'trig',
                'wbc', 'white blood cell', 'leucocyte',
                'rbc', 'red blood cell', 'erythrocyte',
                'platelet', 'plt',
                'alt', 'sgpt', 'alanine',
                'ast', 'sgot', 'aspartate',
                'bilirubin', 'bili',
                'albumin', 'alb',
                'protein',
                'urea', 'bun',
                'sodium', 'na',
                'potassium', 'k',
                'chloride', 'cl'
            ]
            
            print(f"\nSearching for parameter names (case-insensitive):")
            text_lower = text.lower()
            found_params = []
            for param in common_params:
                if param in text_lower:
                    # Find context around the parameter
                    idx = text_lower.find(param)
                    start = max(0, idx - 50)
                    end = min(len(text), idx + 100)
                    context = text[start:end].replace('\n', ' ')
                    found_params.append((param, context))
            
            if found_params:
                print(f"\n✅ Found {len(found_params)} potential parameters:")
                for param, context in found_params[:5]:  # Show first 5
                    print(f"  - {param}: ...{context}...")
            else:
                print("\n❌ No common parameter names found")
                
        except Exception as e:
            print(f"\n❌ Error processing file: {e}")

if __name__ == "__main__":
    analyze_failed_files()
