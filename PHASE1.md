# Phase 1 – OCR-Based Medical Report Ingestion

## Objective
The objective of Phase 1 was to design and implement a reliable OCR pipeline capable of converting medical blood report PDFs into machine-readable text. This phase establishes the foundation for downstream analysis, structured extraction, and automated diagnostics.

---

## Scope of Work
- Environment setup and dependency management  
- PDF-to-image conversion  
- Optical Character Recognition (OCR)  
- Error handling and robustness  
- Modular and testable code structure  

---

## Technical Implementation

### 1. Development Environment
- **Platform:** Windows  
- **Language:** Python  
- **IDE:** VS Code  
- Virtual environment created for dependency isolation  
- Modular project structure following software engineering best practices  

### 2. OCR Pipeline
The following pipeline was implemented:

PDF Input  
→ PDF-to-Image Conversion (using pdf2image)  
→ Text Extraction (using Tesseract OCR via pytesseract)  
→ Raw Text Output  


### 3. Tools and Libraries
- pytesseract  
- pdf2image  
- Pillow  
- Tesseract OCR (configured via system PATH)  
- Poppler (for PDF processing)  

---

## Challenges Faced and Resolutions
- PATH configuration issues for Tesseract and Poppler on Windows  
- PDF conversion failures due to missing Poppler binaries  
- Python module import errors due to incorrect package structure  

**Resolutions:**  
All issues were resolved through proper environment configuration, modular restructuring, and systematic debugging.

---

## Output of Phase 1
- Successfully extracted raw text from blood report PDFs  
- OCR output verified using test scripts  
- OCR text persisted in files for downstream processing  

---

## Phase 1 Deliverables
- End-to-end OCR pipeline  
- Modular Python codebase  
- OCR validation test scripts  
- Documented design and implementation decisions  

---

## Status
**Phase 1 is completed and validated.**  
The system is ready for text preprocessing and structured data extraction.
