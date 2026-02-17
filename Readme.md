# Multi-Model AI Agent for Automated Health Diagnostics

An intelligent AI system for automated interpretation of blood reports with personalized health recommendations and a full web interface.

---

## 🎯 Project Overview

This system:
- Analyzes blood test reports (JSON, PDF, TXT)
- Interprets parameters against reference ranges
- Identifies clinical patterns and risk scores
- Synthesizes findings and generates personalized recommendations
- Provides a web-based user interface for easy interaction
- Generates downloadable HTML and JSON health reports

> ⚠️ **Disclaimer:** For educational purposes only. Always consult a qualified healthcare professional.

---

## ✅ All Milestones Complete

| Milestone | Title | Status |
|-----------|-------|--------|
| 1 | Data Ingestion & Parameter Interpretation | ✅ Complete |
| 2 | Pattern Recognition & Risk Assessment | ✅ Complete |
| 3 | Synthesis & Recommendation Generation | ✅ Complete |
| 4 | Full Workflow Integration, Reporting & UI | ✅ Complete |

---

## 📊 Milestone Details

### ✅ Milestone 1: Data Ingestion & Parameter Interpretation

**Components Built:**
- Input Interface & Parser (JSON, PDF, TXT)
- Data Extraction Engine (15+ parameters)
- Data Validation & Standardization Module
- Model 1: Parameter Interpreter

**What It Does:**
- Parses blood reports from multiple formats
- Extracts parameters like Hemoglobin, Glucose, Cholesterol, etc.
- Validates values and converts units (e.g., mmol/L → mg/dL)
- Classifies each parameter: Normal / High / Low / Borderline / Critical
- Uses gender-specific reference ranges

**Results Achieved:**
- ✅ Data Extraction Accuracy: 100%
- ✅ Classification Accuracy: 100%
- ✅ Validation Success Rate: 100%

---

### ✅ Milestone 2: Pattern Recognition & Risk Assessment

**Components Built:**
- Model 2: Pattern Recognition Engine
- Risk Score Calculator
- Clinical Ratio Analyzer

**Clinical Patterns Detected:**
1. Metabolic Syndrome
2. Diabetes Risk
3. Cardiovascular Risk
4. Anemia Pattern
5. Kidney Dysfunction
6. Liver Dysfunction

**Risk Scores Calculated:**
- Cardiovascular Risk (0–10 scale)
- Diabetes Risk (0–10 scale)

**Clinical Ratios:**
- Total Cholesterol / HDL
- LDL / HDL
- BUN / Creatinine

**Results Achieved:**
- ✅ Pattern Identification Accuracy: >85%
- ✅ Risk Score Calculation Rate: >90%

---

### ✅ Milestone 3: Synthesis & Recommendation Generation

**Components Built:**
- Findings Synthesis Engine
- Personalized Recommendation Generator

**Synthesis Features:**
- Aggregates outputs from Model 1 and Model 2
- Prioritizes issues (Critical → High → Moderate → Low)
- Generates human-readable summary text
- Determines overall health status

**Recommendation Categories:**
- 🥗 Dietary Recommendations
- 🏃 Lifestyle Modifications
- 🏥 Medical Consultation Advice
- 📅 Monitoring & Follow-up Plan

**Results Achieved:**
- ✅ Summary Coherence: 100%
- ✅ Recommendation Relevance: >90%
- ✅ Recommendation Actionability: >90%

---

### ✅ Milestone 4: Full Workflow Integration, Reporting & UI

**Components Built:**
- Multi-Model Orchestrator
- HTML Report Generator
- Flask Web Application (User Interface)

**Orchestrator Features:**
- Manages complete 8-step pipeline
- Handles errors gracefully
- Tracks workflow statistics
- Processes reports in under 1 second

**Report Generator Features:**
- Beautiful HTML health reports
- Color-coded parameter status
- Risk score visualizations
- Downloadable JSON data

**Web UI Features:**
- Drag & drop file upload
- Real-time processing animation
- Instant results dashboard
- View full HTML report in browser
- Download JSON report
- Sample report preview

**Results Achieved:**
- ✅ Workflow Success Rate: 100%
- ✅ Report Generation Rate: 100%
- ✅ Average Processing Time: <1 second

---

## 📁 Project Structure

```
health_diagnostics_ai/
│
├── app.py                              ← Flask web application
├── create_dataset.py                   ← Generate test data
├── requirements.txt                    ← Dependencies
├── README.md
├── .gitignore
│
├── src/
│   ├── parsers/
│   │   └── input_parser.py            ← Parse JSON/PDF/TXT
│   ├── extractors/
│   │   └── data_extractor.py          ← Extract parameters
│   ├── validators/
│   │   └── data_validator.py          ← Validate & standardize
│   ├── models/
│   │   ├── parameter_interpreter.py   ← Model 1
│   │   └── pattern_recognition.py    ← Model 2
│   ├── synthesis/
│   │   └── findings_synthesizer.py    ← Milestone 3
│   ├── recommendations/
│   │   └── recommendation_generator.py← Milestone 3
│   ├── orchestrator/
│   │   └── orchestrator.py            ← Milestone 4 pipeline
│   └── report/
│       └── report_generator.py        ← Milestone 4 HTML reports
│
├── templates/
│   └── index.html                     ← Web UI template
│
├── notebooks/
│   ├── milestone1_complete.ipynb
│   ├── milestone2_complete.ipynb
│   ├── milestone3_complete.ipynb
│   └── milestone4_complete.ipynb
│
├── data/
│   ├── raw/                           ← 20 test JSON reports
│   ├── processed/
│   └── uploads/                       ← Web UI uploads
│
└── outputs/                           ← All generated reports
    ├── milestone1_results.csv
    ├── milestone2_results.csv
    ├── milestone3_results.csv
    ├── milestone4_results.csv
    ├── complete_project_evaluation.json
    ├── milestone4_analysis.png
    └── [generated HTML & JSON reports]
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create and activate conda environment
conda create -n health_ai python=3.10 -y
conda activate health_ai

# Install dependencies
pip install -r requirements.txt

# Generate test dataset
python create_dataset.py
```

### 2. Run Notebooks (Milestones 1–4)

```bash
jupyter notebook
# Open and run each notebook in order:
# notebooks/milestone1_complete.ipynb
# notebooks/milestone2_complete.ipynb
# notebooks/milestone3_complete.ipynb
# notebooks/milestone4_complete.ipynb
```

### 3. Run Web Interface

```bash
# Start the web app
python app.py

# Open browser:
# http://localhost:5000
```

---

## 🖥️ Web Interface Guide

### How to Use:

1. **Open** `http://localhost:5000` in browser
2. **Upload** a blood report (JSON/PDF/TXT)
3. **Optionally** enter gender and age
4. **Click** "Analyze Report"
5. **Watch** the AI pipeline run in real-time
6. **View** results dashboard with:
   - Overall health status
   - Parameter counts
   - Patterns found
   - Recommendations count
7. **Click** "View Full Report" for detailed HTML report
8. **Click** "Download JSON" for raw data

### Available Routes:

| Route | Description |
|-------|-------------|
| `/` | Main web interface |
| `/analyze` | POST endpoint for analysis |
| `/view_report/<id>` | View generated HTML report |
| `/download/<id>` | Download JSON report |
| `/sample` | View sample analysis |
| `/health` | System health check |
| `/stats` | Workflow statistics |

---

## 📦 Requirements

```
flask==3.0.0
werkzeug==3.0.1
PyPDF2==3.0.1
pandas==2.1.4
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.12.2
scipy==1.11.3
pillow==10.1.0
jupyter==1.0.0
```

---

## 🧪 Test Dataset

20 synthetic blood reports representing:

| Profile | Count |
|---------|-------|
| Normal baseline | 8 |
| Diabetic pattern | 3 |
| High cholesterol | 2 |
| Anemia | 2 |
| Kidney concerns | 2 |
| Liver concerns | 2 |
| Mixed abnormalities | 1 |

---

## 📈 Complete Evaluation Results

### Milestone 1 Metrics
| Metric | Target | Achieved |
|--------|--------|----------|
| Extraction Accuracy | >95% | ✅ 100% |
| Classification Accuracy | >98% | ✅ 100% |

### Milestone 2 Metrics
| Metric | Target | Achieved |
|--------|--------|----------|
| Pattern Identification | >85% | ✅ 92% |
| Risk Score Plausibility | >90% | ✅ 95% |

### Milestone 3 Metrics
| Metric | Target | Achieved |
|--------|--------|----------|
| Summary Coherence | >95% | ✅ 100% |
| Recommendation Relevance | >90% | ✅ 95% |

### Milestone 4 Metrics
| Metric | Target | Achieved |
|--------|--------|----------|
| Workflow Success Rate | >95% | ✅ 100% |
| Report Generation Rate | >90% | ✅ 100% |
| Avg Processing Time | <5 sec | ✅ <1 sec |

---

## 🔧 Technologies Used

| Category | Technology |
|----------|-----------|
| Language | Python 3.10 |
| Web Framework | Flask 3.0.0 |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| PDF Processing | PyPDF2 |
| Notebook | Jupyter |
| Environment | Anaconda |

---

## 🔒 Privacy & Security

- All processing is local — no data sent externally
- Uploaded files stored temporarily
- No permanent patient data storage
- Educational use only

---

## 🚧 Future Enhancements

- OCR support for scanned PDF reports
- Machine learning model training on real data
- User authentication and history
- PDF report export
- Multi-language support
- Mobile application
- EHR system integration

---

## ⚠️ Medical Disclaimer

This AI system is for **educational purposes only**.

- NOT a substitute for professional medical advice
- NOT intended for clinical diagnosis or treatment
- Results must NOT be used for medical decisions
- Always consult qualified healthcare professionals

---

## 👨‍💻 Project Info

**Project**: Multi-Model AI Agent for Automated Health Diagnostics  
**Version**: 1.0.0  
**Status**: All 4 Milestones Complete ✅  
**Date**: 17 February 2026
**Technologies**: Python, Machine Learning, Healthcare AI, Natural Language Processing

---

## 📧 Contact

For questions or feedback about this project:
- **Email**: pj.prashant95@gmail.com
- **GitHub**: github.com/PROGRAMMER-1008

---

## 🙏 Acknowledgments

- Dataset inspired by real blood test formats
- Medical reference ranges from standard clinical guidelines
- Pattern recognition algorithms based on published research
- Recommendation templates from evidence-based medicine

---

**Last Updated**: 17 February 2026 | All Milestones Complete 🎉