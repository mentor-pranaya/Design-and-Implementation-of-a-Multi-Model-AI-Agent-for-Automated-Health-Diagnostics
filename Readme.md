# Multi-Model AI Agent for Automated Health Diagnostics
## Milestone 1: Data Ingestion & Parameter Interpretation

This project implements an intelligent system for analyzing blood test reports using AI.

---

## 🎯 Milestone 1 Objectives

- ✅ Implement Input Interface & Parser (PDF/JSON support)
- ✅ Develop Data Extraction Engine
- ✅ Build Data Validation & Standardization Module
- ✅ Implement Model 1: Parameter Interpretation

### Success Criteria
- Data Extraction Accuracy: **>95%**
- Parameter Classification Accuracy: **>98%**

---

## 📁 Project Structure

```
health_diagnostics_ai/
├── data/
│   ├── raw/                    # Test blood reports (JSON)
│   ├── processed/              # Processed data
│   └── test_reports/           # Additional test cases
├── src/
│   ├── parsers/
│   │   └── input_parser.py     # Parse PDF/JSON/TXT reports
│   ├── extractors/
│   │   └── data_extractor.py   # Extract blood parameters
│   ├── validators/
│   │   └── data_validator.py   # Validate & standardize data
│   └── models/
│       └── parameter_interpreter.py  # Model 1: Classify parameters
├── notebooks/
│   └── milestone1_complete.ipynb    # Main evaluation notebook
├── outputs/                    # Evaluation results
├── tests/                      # Unit tests
├── create_dataset.py          # Dataset generator
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🚀 Quick Start Guide

### Step 1: Environment Setup

```bash
# Clone or download the project
cd health_diagnostics_ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Generate Test Dataset

```bash
# Generate 20 synthetic blood reports
python create_dataset.py
```

This creates:
- 20 JSON blood reports in `data/raw/`
- Summary CSV at `data/raw/reports_summary.csv`
- Mix of normal and abnormal profiles

### Step 3: Run Milestone 1 Evaluation

```bash
# Start Jupyter Notebook
jupyter notebook

# Open: notebooks/milestone1_complete.ipynb
# Run all cells (Cell → Run All)
```

### Step 4: Review Results

Check the outputs:
- `outputs/milestone1_results.csv` - Processing results for all reports
- `outputs/milestone1_evaluation_report.json` - Comprehensive evaluation metrics

---

## 📊 Understanding the Components

### 1. Input Parser (`src/parsers/input_parser.py`)

**Purpose:** Accept blood reports in multiple formats

**Supported Formats:**
- JSON (structured data)
- PDF (with text extraction)
- TXT (plain text)

**Usage:**
```python
from parsers.input_parser import InputParser

parser = InputParser()
parsed_data = parser.parse('data/raw/report_001.json')
```

### 2. Data Extractor (`src/extractors/data_extractor.py`)

**Purpose:** Extract blood parameters, values, units, and reference ranges

**Features:**
- Recognizes 15+ common blood parameters
- Handles parameter name variations (e.g., "Hemoglobin", "HB", "Hgb")
- Standardizes parameter names and units

**Usage:**
```python
from extractors.data_extractor import ParameterExtractor

extractor = ParameterExtractor()
parameters = extractor.extract(parsed_data)
```

### 3. Data Validator (`src/validators/data_validator.py`)

**Purpose:** Validate and standardize extracted data

**Validations:**
- Value plausibility checks
- Unit conversions (e.g., mmol/L → mg/dL)
- Reference range validation
- Completeness checking

**Usage:**
```python
from validators.data_validator import DataValidator

validator = DataValidator()
validated_params, report = validator.validate_and_standardize(parameters)
```

### 4. Parameter Interpreter (`src/models/parameter_interpreter.py`)

**Purpose:** Classify parameters as normal, high, low, borderline, or critical

**Classifications:**
- Normal
- High / Low
- Borderline High / Borderline Low
- Critical High / Critical Low

**Features:**
- Gender-specific reference ranges
- Deviation percentage calculation
- Human-readable interpretation messages

**Usage:**
```python
from models.parameter_interpreter import ParameterInterpreter

interpreter = ParameterInterpreter(gender='male', age=45)
interpretations = interpreter.interpret(validated_params)
```

---

## 🧪 Running Tests

### Test Individual Components

```python
# In Python or Jupyter

# Test Parser
from parsers.input_parser import InputParser
parser = InputParser()
data = parser.parse('data/raw/report_001.json')
print(f"Parsed {len(data['parameters'])} parameters")

# Test Extractor
from extractors.data_extractor import ParameterExtractor
extractor = ParameterExtractor()
params = extractor.extract(data)
print(f"Extracted {len(params)} parameters")

# Test Validator
from validators.data_validator import DataValidator
validator = DataValidator()
validated, report = validator.validate_and_standardize(params)
print(validator.get_validation_summary())

# Test Interpreter
from models.parameter_interpreter import ParameterInterpreter
interpreter = ParameterInterpreter(gender='male')
interpretations = interpreter.interpret(validated)
print(interpreter.get_summary())
```

### Run End-to-End Pipeline

```python
def process_report(file_path):
    # Parse
    parser = InputParser()
    parsed = parser.parse(file_path)
    
    # Extract
    extractor = ParameterExtractor()
    extracted = extractor.extract(parsed)
    
    # Validate
    validator = DataValidator()
    validated, _ = validator.validate_and_standardize(extracted)
    
    # Interpret
    interpreter = ParameterInterpreter(
        gender=parsed.get('gender'),
        age=parsed.get('age')
    )
    interpretations = interpreter.interpret(validated)
    
    return interpretations

# Process a report
results = process_report('data/raw/report_001.json')
```

---

## 📈 Evaluation Metrics

The notebook calculates these metrics:

1. **Data Extraction Accuracy**
   - Formula: (Extracted Parameters / Expected Parameters) × 100
   - Target: >95%

2. **Validation Success Rate**
   - Formula: (Valid Parameters / Total Parameters) × 100
   - Indicates data quality

3. **Classification Accuracy**
   - Formula: Correct Classifications / Total Classifications × 100
   - Target: >98%

---

## 🔧 Customization

### Adding New Blood Parameters

Edit `src/extractors/data_extractor.py`:

```python
PARAMETER_ALIASES = {
    'your_parameter': ['alias1', 'alias2'],
    # ... existing parameters
}
```

Edit `src/validators/data_validator.py`:

```python
PLAUSIBILITY_RANGES = {
    'YOUR_PARAMETER': {'min': X, 'max': Y, 'unit': 'unit'},
    # ... existing ranges
}
```

Edit `src/models/parameter_interpreter.py`:

```python
STANDARD_REFERENCE_RANGES = {
    'YOUR_PARAMETER': {'min': X, 'max': Y, 'unit': 'unit'},
    # ... existing ranges
}
```

### Adjusting Reference Ranges

Modify the reference ranges in `src/models/parameter_interpreter.py` to match your requirements or regional guidelines.

---

## 📝 Sample Output

```
MILESTONE 1 EVALUATION RESULTS
================================================================

Total Reports Processed: 20
Errors: 0
Success Rate: 100.0%

MILESTONE 1 SUCCESS METRICS
================================================================

1. Data Extraction Accuracy: 100.0%
   Target: >95% | Status: ✓ PASS

2. Validation Success Rate: 100.0%

3. Classification Accuracy: 100.0%
   Target: >98% | Status: ✓ PASS

================================================================
🎉 MILESTONE 1: PASSED
================================================================
```

---

## 🐛 Troubleshooting

### Issue: Module Import Errors

```bash
# Ensure you're in the project root
cd health_diagnostics_ai

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Dataset Not Found

```bash
# Regenerate dataset
python create_dataset.py
```

### Issue: Jupyter Kernel Not Found

```bash
# Install Jupyter kernel
python -m ipykernel install --user --name=venv
```

---

## 📤 GitHub Deployment

### Step 1: Initialize Git Repository

```bash
# Initialize repository
git init

# Add all files
git add .

# Commit
git commit -m "Milestone 1: Data Ingestion & Parameter Interpretation complete"
```

### Step 2: Create GitHub Repository

1. Go to GitHub.com
2. Click "New Repository"
3. Name it: `health-diagnostics-ai`
4. Don't initialize with README (we have one)

### Step 3: Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/health-diagnostics-ai.git

# Create and switch to main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 4: Create Milestone 1 Branch

```bash
# Create branch
git checkout -b milestone-1

# Push branch
git push -u origin milestone-1
```

---

## 🎓 Next Steps (Milestone 2)

The next milestone will implement:
- Model 2: Pattern Recognition & Risk Assessment
- Model 3: Contextual Analysis (optional)
- Integration of multiple models

---

## 📜 License

This is an educational project for demonstrating AI-driven health diagnostics.

**Disclaimer:** This system is for educational purposes only and should not be used for actual medical diagnosis. Always consult qualified healthcare professionals.

---

## 👨‍💻 Development Notes

### Code Quality
- All modules include comprehensive docstrings
- Type hints used throughout
- Logging implemented for debugging
- Error handling with meaningful messages

### Testing Strategy
- Component-level testing
- Integration testing
- End-to-end pipeline validation
- Automated metrics calculation

---

## 📧 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the notebook comments
3. Examine the sample outputs
4. Test individual components in isolation

---

**Project Status:** ✅ Milestone 1 Complete

**Last Updated:** January 2026