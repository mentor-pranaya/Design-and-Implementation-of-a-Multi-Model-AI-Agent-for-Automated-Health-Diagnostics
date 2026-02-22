"""Check if report 7 has multiple pages with actual results"""
import PyPDF2
from pathlib import Path

report_path = Path(r"C:\Users\mi\Downloads\infosys project\data\test_reports\test report (7).pdf")

# Check number of pages
with open(report_path, 'rb') as f:
    pdf = PyPDF2.PdfReader(f)
    num_pages = len(pdf.pages)
    
    print("="*80)
    print(f"REPORT 7 ANALYSIS")
    print("="*80)
    print(f"Total pages: {num_pages}")
    
    # Extract text from each page
    for page_num in range(num_pages):
        print(f"\n{'='*80}")
        print(f"PAGE {page_num + 1}")
        print(f"{'='*80}")
        
        page = pdf.pages[page_num]
        text = page.extract_text()
        
        print(f"Text length: {len(text)} characters")
        print(f"\nContent preview:")
        print("-"*80)
        print(text[:1000])
        print("-"*80)
        
        # Look for test parameters
        text_lower = text.lower()
        params_found = []
        
        test_params = ['glucose', 'uric acid', 'sodium', 'potassium', 'chloride', 
                      'creatinine', 'urea', 'hemoglobin', 'wbc', 'rbc']
        
        for param in test_params:
            if param in text_lower:
                params_found.append(param)
        
        if params_found:
            print(f"\n✅ Found parameters: {', '.join(params_found)}")
        else:
            print(f"\n⚠️  No test parameters found on this page")
