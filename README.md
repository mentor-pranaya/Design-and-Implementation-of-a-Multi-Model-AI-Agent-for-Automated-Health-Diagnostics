# Multi-Model AI Health Diagnostics System

An intelligent AI system for automated interpretation of blood reports and personalized health recommendations.

## 🎯 Features

- 📄 **Multi-format support** - PDF, Images, JSON
- 🔍 **Advanced OCR** - Extract data from scanned reports
- 🧠 **Multi-model AI analysis** - Parameter interpretation, pattern recognition, contextual analysis
- 📊 **Risk assessment** - Cardiovascular, diabetes, kidney health
- 💡 **Personalized recommendations** - Diet, lifestyle, medical follow-up
- 🔒 **HIPAA-compliant architecture** - Security and privacy by design

## 📁 Project Structure

```
infosys project/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── api/                      # API endpoints
│   │   │   └── endpoints/
│   │   │       └── reports.py        # Report management endpoints
│   │   ├── core/                     # Core configuration
│   │   │   └── config.py            # Application settings
│   │   ├── models/                   # Database models
│   │   │   ├── database.py          # Database connection
│   │   │   └── report.py            # BloodReport, UserContext models
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   └── report.py            # Request/response schemas
│   │   ├── services/                 # Business logic
│   │   │   ├── input_parser/        # File parsing (PDF, image, JSON)
│   │   │   ├── data_extraction/     # OCR and data extraction
│   │   │   ├── validation/          # Data validation
│   │   │   ├── model_1_interpretation/  # Parameter interpretation
│   │   │   ├── model_2_pattern/     # Pattern recognition
│   │   │   ├── model_3_context/     # Contextual analysis
│   │   │   ├── synthesis/           # Findings synthesis
│   │   │   ├── recommendation/      # Recommendation generation
│   │   │   └── orchestrator/        # Workflow orchestration
│   │   └── utils/                    # Utility functions
│   ├── tests/                        # Backend tests
│   ├── alembic/                      # Database migrations (to be created)
│   ├── .env.example                  # Environment variables template
│   ├── requirements.txt              # Python dependencies
│   └── init_db.py                   # Database initialization script
├── data/                             # Data storage
│   ├── sample_reports/              # Sample blood reports
│   ├── test_reports/                # Test datasets
│   ├── reference_ranges/            # Medical reference ranges
│   ├── uploads/                     # User uploaded files
│   └── processed/                   # Processed reports
├── logs/                             # Application logs
├── docs/                             # Documentation
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **PostgreSQL 14+** (or SQLite for development)
- **Redis** (optional, for background tasks)

### 1. Setup Virtual Environment

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy example environment file
copy .env.example .env

# Edit .env with your settings
# - Set DATABASE_URL
# - Set SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_hex(32))")
# - Set OPENAI_API_KEY (if using LLM features)
```

### 4. Setup Database

**Option A: PostgreSQL (Recommended)**

```powershell
# Install PostgreSQL if not already installed
# Then create database
psql -U postgres
CREATE DATABASE health_diagnostics;
\q

# Update DATABASE_URL in .env:
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/health_diagnostics
```

**Option B: SQLite (Development only)**

```powershell
# Update DATABASE_URL in .env:
# DATABASE_URL=sqlite:///./health_diagnostics.db
```

### 5. Initialize Database Tables

```powershell
python init_db.py
```

### 6. Run the Application

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the API

- **Swagger UI (Interactive docs)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## 📚 API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check

### Reports
- `POST /api/v1/reports/upload` - Upload blood report for analysis
- `GET /api/v1/reports/{report_id}` - Get analysis results
- `GET /api/v1/reports/` - List all reports (paginated)

## 🗓️ Development Milestones

### ✅ Milestone 0: Foundation (COMPLETED)
- [x] Project structure setup
- [x] Core configuration
- [x] Database models
- [x] API scaffolding
- [x] Pydantic schemas

### 🔄 Milestone 1: Data Ingestion (Weeks 1-2) - IN PROGRESS
- [ ] Input parser implementation (PDF, image, JSON)
- [ ] OCR integration (EasyOCR, Tesseract)
- [ ] Data extraction engine
- [ ] Validation & standardization module
- [ ] Model 1: Parameter interpretation
- [ ] Test with 15-20 sample reports
- **Target**: >95% extraction accuracy, >98% classification accuracy

### ⏳ Milestone 2: Pattern Recognition (Weeks 3-4)
- [ ] Model 2: Pattern recognition & risk assessment
- [ ] Model 3: Contextual analysis (age/gender adjustments)
- [ ] Integration of Models 1, 2, 3
- [ ] Confidence scoring
- **Target**: >85% pattern identification, >90% risk score plausibility

### ⏳ Milestone 3: Synthesis & Recommendations (Weeks 5-6)
- [ ] Findings synthesis engine
- [ ] Personalized recommendation generator
- [ ] Report formatting module
- **Target**: >95% summary accuracy, >90% recommendation relevance

### ⏳ Milestone 4: Full Integration (Weeks 7-8)
- [ ] Multi-model orchestrator
- [ ] End-to-end workflow
- [ ] Frontend development (React)
- [ ] Testing & validation
- [ ] Deployment preparation
- **Target**: >95% workflow success rate

## 🧪 Testing

```powershell
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ -v --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

## 📊 Database Schema

### BloodReport Table
- Stores uploaded reports, extracted data, analysis results
- Tracks processing status and confidence scores
- JSON fields for flexible data storage

### UserContext Table
- Stores user demographics and medical history
- Used for personalized analysis (Model 3)

## 🔧 Configuration

Key settings in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/health_diagnostics

# Security
SECRET_KEY=your-secret-key-32-characters-minimum

# AI/ML
OPENAI_API_KEY=sk-...  # Optional
OCR_GPU=False          # Set True if GPU available

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB

# Logging
LOG_LEVEL=INFO
```

## 🛡️ Security & Compliance

### HIPAA Considerations
- ✅ Encryption at rest and in transit (TLS 1.2+)
- ✅ Audit logging for all data access
- ✅ Configurable data retention policies
- ⚠️ Requires Business Associate Agreement (BAA) with cloud providers
- ⚠️ Regular security assessments needed

### Medical Disclaimer
⚠️ **IMPORTANT**: This system is for **informational and educational purposes only**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions regarding medical conditions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

[Your License Here]

## 🆘 Troubleshooting

### Database Connection Issues
```powershell
# Test PostgreSQL connection
psql -U postgres -h localhost -d health_diagnostics

# Check if tables were created
python -c "from app.models.database import engine; print(engine.table_names())"
```

### Import Errors
```powershell
# Ensure you're in the backend directory and venv is activated
cd backend
.\venv\Scripts\activate

# Verify installation
pip list | findstr fastapi
```

### Port Already in Use
```powershell
# Change port in command
uvicorn app.main:app --reload --port 8001
```

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Current Status**: Foundation complete ✅ | Ready for Milestone 1 implementation 🚀
