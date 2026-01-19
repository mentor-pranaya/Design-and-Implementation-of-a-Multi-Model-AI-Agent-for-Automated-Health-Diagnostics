# Phase 2 – Text Processing and Structured Data Extraction

## Objective
The objective of Phase 2 was to convert noisy OCR output into structured, medically meaningful data that can be used for automated diagnostic reasoning.

---

## Scope of Work

- OCR text cleaning and normalization
- Rule-based extraction of key blood parameters
- Unit normalization
- Domain-aware medical validation
- End-to-end pipeline integration

---

## Text Cleaning

OCR output often contains noise such as inconsistent spacing, line breaks, and artifacts.  
A text cleaning module was implemented to:

- Normalize line endings
- Remove excessive whitespace
- Remove non-informative OCR artifacts
- Ensure clean, consistent text for extraction

---

## Structured Parameter Extraction

### Extracted Parameters
- Hemoglobin
- White Blood Cell (WBC) Count
- Platelet Count

### Extraction Method
- Regular expression–based pattern matching
- Parameter-specific extraction logic
- Unit normalization for consistency

Example structured output:
```python
{
  "Hemoglobin": {"value": 14.5, "unit": "g/dL"},
  "WBC": {"value": 10570.0, "unit": "cells/mm3"},
  "Platelet Count": {"value": 915000.0, "unit": "cells/mm3"}
}
