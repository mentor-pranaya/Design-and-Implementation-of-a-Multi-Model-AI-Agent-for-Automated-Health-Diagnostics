# 🩺 MedAura — Personal Health Intelligence Dashboard

MedAura is a privacy-first health analytics app that converts raw medical lab reports into clear trends and insights.  
Upload a lab report (PDF or image), and MedAura extracts key biomarkers, tracks them over time, and helps users understand how their health is changing.

No cloud uploads. No black boxes. Your data stays local.

---

## 🚀 What MedAura Does

- Reads medical lab reports (PDFs and images)
- Extracts important biomarkers using OCR + text parsing
- Stores health data locally using SQLite
- Tracks changes over time with trend analysis
- Displays interactive and intuitive visualizations
- Protects user data with secure authentication

---

## 🧠 Architecture Overview (MVC-Style)

MedAura follows a Streamlit-friendly MVC-inspired architecture.

### Model
- User accounts and authentication data
- Health logs and biomarker history
- Trend and delta analysis logic
- Reference ranges and health rules

### View
- Sidebar authentication UI
- Dashboard layout and biomarker cards
- Trend charts and history tables

### Controller
- Application flow and routing
- User actions (login, upload, analyze)
- Session state coordination

---

## 📁 Project Structure

medaura/

│

├── app.py # Controller (application flow)

│

├── models/ # Data & business logic

│ ├── database

│ ├── auth

│ └── health

│

├── services/ # OCR & report processing

│ ├── ocr

│ └── report_parser

│

├── views/ # UI components

│ ├── sidebar

│ ├── dashboard

│ └── history

│

├── utils/ # Helpers & constants

│ ├── security

│ └── constants

│

└── requirements.txt


---

## 📊 Visual Design Principles

### Biomarker Summary Cards
- Show latest value
- Indicate trend (increase, decrease, stable)
- Color-coded health status
  - Green: stable or improving
  - Amber: gradual change
  - Red: sudden spike or risk

### Trend Visualization
- Unified time-series chart
- Biomarkers distinguished by color
- Reference ranges shown as subtle bands
- Interactive hover for precise values

### Progressive Disclosure
1. Summary cards for instant understanding  
2. Trend chart for pattern recognition  
3. Raw data table for verification  

---

## 🔐 Privacy & Security

- Local-only data storage (SQLite)
- No external APIs
- No cloud uploads
- Password hashing for authentication
- OCR and processing run on-device

---

## ⚙️ How the App Works

1. User logs in or signs up
2. Uploads a lab report (PDF/image)
3. Text is extracted (OCR fallback if needed)
4. Biomarkers are parsed from text
5. Values are stored with timestamps
6. Trends are calculated from history
7. Insights are displayed visually

---

## 🧩 Extensibility

The architecture supports:
- Adding new biomarkers
- Expanding reference ranges
- Alerting for unsafe values
- ML-based anomaly detection
- Doctor-ready report exports
- Mobile-friendly views

All without restructuring the app.

---

## ⚠️ Disclaimer

MedAura is not a medical diagnostic tool.  
It is intended for personal tracking and trend visualization only and should not replace professional medical advice.

---

## 👤 Author

Built with a focus on:
- Explainable AI
- Clean engineering
- Data ownership
- Practical health analytics

---

## 🛣️ Future Roadmap

- Reference range alerts
- Health baseline scoring
- PDF health summaries
- Advanced trend analytics
- Deployment-ready production setup

---

MedAura is designed to grow—from a solid foundation to a real-world health intelligence system.
