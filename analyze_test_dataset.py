"""
Analyze the test dataset to understand what reports we have
and prepare for evaluation.
"""

import os
import glob

def analyze_test_dataset():
    test_dir = "data/test_reports"
    
    print("=" * 80)
    print("TEST DATASET ANALYSIS")
    print("=" * 80)
    
    # Get all files
    all_files = os.listdir(test_dir)
    pdf_files = [f for f in all_files if f.endswith('.pdf')]
    png_files = [f for f in all_files if f.endswith('.png')]
    
    print(f"\nDataset Summary:")
    print(f"Total files: {len(all_files)}")
    print(f"PDF reports: {len(pdf_files)}")
    print(f"PNG reports: {len(png_files)}")
    
    print(f"\nPDF Reports ({len(pdf_files)}):")
    for i, pdf in enumerate(sorted(pdf_files), 1):
        print(f"  {i:2d}. {pdf}")
    
    print(f"\nPNG Reports ({len(png_files)}):")
    for i, png in enumerate(sorted(png_files), 1):
        print(f"  {i:2d}. {png}")
    
    # Check for duplicates (same number in PDF and PNG)
    pdf_numbers = set()
    png_numbers = set()
    
    for pdf in pdf_files:
        # Extract number from filename like "test report (1).pdf"
        try:
            num = pdf.split('(')[1].split(')')[0]
            pdf_numbers.add(num)
        except:
            pass
    
    for png in png_files:
        # Extract number from filename like "test report (1).png"
        try:
            num = png.split('(')[1].split(')')[0]
            png_numbers.add(num)
        except:
            pass
    
    duplicates = pdf_numbers.intersection(png_numbers)
    if duplicates:
        print(f"\nDuplicate Numbers (both PDF and PNG): {sorted(duplicates)}")
        print("Note: These might be the same report in different formats")
    
    # Count unique reports
    unique_numbers = pdf_numbers.union(png_numbers)
    print(f"\nUnique Report Numbers: {len(unique_numbers)}")
    print(f"Numbers: {sorted(unique_numbers)}")
    
    # Project requirement check
    print(f"\n" + "=" * 80)
    print("PROJECT REQUIREMENT CHECK")
    print("=" * 80)
    print(f"Required: 15-20 diverse blood reports")
    print(f"You have: {len(unique_numbers)} unique reports")
    
    if len(unique_numbers) >= 15:
        print("✅ REQUIREMENT MET - You have enough reports!")
        if len(unique_numbers) >= 20:
            print("🎉 EXCEEDS REQUIREMENT - Excellent dataset size!")
    else:
        print(f"⚠️  Need {15 - len(unique_numbers)} more reports to meet minimum")
    
    print(f"\nFormat Diversity:")
    print(f"✅ PDF format: {len(pdf_files)} reports")
    if len(png_files) > 0:
        print(f"✅ PNG format: {len(png_files)} reports")
        print("✅ Multiple formats - Good for testing OCR robustness")
    
    print(f"\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. ✅ Test dataset collection: COMPLETE")
    print("2. ⏳ Run OCR on all reports to extract data")
    print("3. ⏳ Create ground truth annotations")
    print("4. ⏳ Run evaluation script")
    print("5. ⏳ Generate metrics report")
    
    print(f"\nRecommended Action:")
    print("Run the evaluation pipeline on these reports to get your metrics!")
    
    return len(unique_numbers), pdf_files, png_files

if __name__ == "__main__":
    analyze_test_dataset()