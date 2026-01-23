__AI Multi-Model Health Diagnostic Agent__

An AI-powered multi-model health diagnostic system that analyzes medical reports (PDF / CSV / JSON), extracts health parameters using OCR & NLP, performs risk assessment + pattern recognition, and generates visual charts, personalized recommendations, and downloadable PDF medical reports through an interactive GUI-based application.



__🚀 Project Overview__

This project implements a Multi-Model AI Agent Architecture for automated health diagnostics:

📄 Accepts PDF / CSV / JSON medical reports

🔍 Extracts medical parameters using OCR & NLP

📊 Performs risk assessment & pattern recognition

🤖 Uses an LLM-based reasoning engine

📈 Displays visual charts & trends

📑 Generates downloadable PDF medical reports

🎨 Provides a colorful, user-friendly GUI


__System Architecture__
User → GUI → OCR → Data Extraction → Multi-Model AI
                                 ├─ Model 1: Parameter Interpretation
                                 ├─ Model 2: Risk + Pattern Recognition
                                 ├─ Model 3: Contextual Analysis
                                 ↓
                           LLM Reasoning Engine
                                 ↓
                       Visual Charts + PDF Report

__📁 Folder Structure__
AI_MULTIMODEL_HEALTH_DIAGNOSTIC_AGENT/
│
├── app.py                     # Main GUI application
├── orchestrator.py            # Coordinates all AI models
├── llm_engine.py              # LLM reasoning & explanation engine
├── requirements.txt
│
├── assets/                    # GUI images, icons, backgrounds
│
├── data/
│   └── reference_ranges_age_gender.csv
│
├── models/
│   ├── __init__.py
│   ├── model1_parameter_interpreter.py
│   ├── model2_risk_pattern.py
│   └── model3_contextual_analysis.py
│
├── ocr/
│   ├── __init__.py
│   ├── ocr_reader.py
│   └── pdf_reader.py
│
├── processing/
│   ├── __init__.py
│   └── extractor.py
│
├── report/
│   ├── __init__.py
│   ├── visual_charts.py
│   └── pdf_report_generator.py
│
└── sample_reports/
    ├── csv/
    ├── json/
    └── pdf/



__AI Models Description__
__🔹 Model 1 – Parameter Interpretation__

Interprets lab values

Compares with age & gender-based reference ranges

Flags normal / abnormal parameters

__🔹 Model 2 – Risk Assessment & Pattern Recognition__

Detects health risk levels (Low / Medium / High)

Identifies patterns & anomalies in medical data

Generates personalized health recommendations

__🔹 Model 3 – Contextual Analysis__

Uses patient age, gender, and trends

Adds medical context for better diagnosis


__🤖 LLM Engine__

Converts raw model outputs into human-readable medical explanations

Provides clear summaries, warnings & recommendations

Designed to be extendable to GPT-based APIs

__📊 Visual Charts & Reports__

Bar charts of medical parameters

Trend analysis graphs

Auto-generated PDF medical report

Includes:

Patient summary

Risk analysis

Visual charts

Personalized recommendations

__🎨 GUI Features__

Clean & colorful interface

Upload medical reports

View analysis results instantly
View analysis results instantly

Display charts inside the app

Download PDF report with one click

Uses images/icons from assets/

__🛠 Technologies Used__

Python

Tkinter (GUI)

OCR (Tesseract)

Pandas / NumPy

Matplotlib
