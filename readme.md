# 🩺 INBLOODO AGENT - AI Health Diagnostics

Advanced AI-powered analysis of blood reports with instant recommendations and natural remedies.

## ✨ Features

- **🤖 Intent Inference AI**: Natural language understanding that infers user intent even with vague requests
- **💬 Conversational Interface**: Chat naturally about health concerns with context-aware responses
- **Multi-format Support**: PDF, CSV, JSON, and image files
- **AI-Powered Analysis**: Advanced machine learning models for health risk assessment
- **Instant Recommendations**: Personalized health advice and natural remedies
- **Ambiguity Handling**: Automatically asks clarifying questions when needed
- **Beautiful Web Interface**: Modern, responsive design with real-time animations
- **📄 Professional PDF Reports**: Automatically generate comprehensive medical-grade reports for download
- **Secure API**: Protected endpoints with API key authentication
- **Production Ready**: Optimized for deployment on cloud platforms

## 🚀 Quick Start

### Option 1: One-Click Start (Windows)
```bash
# Double-click start.bat or run in command prompt
start.bat
```

### Option 2: One-Click Start (Linux/Mac)
```bash
# Make executable and run
chmod +x start.sh
./start.sh
```

### Option 3: Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the application
python main.py
```

## 🌐 Access the Application

After starting, open your browser and go to:
- **Web Interface**: http://localhost:10000
- **Health Check**: http://localhost:10000/health
- **API Documentation**: http://localhost:10000/docs (development only)

## 🔑 API Usage

### Authentication
All API endpoints require an API key in the header:
```bash
curl -H "x-api-key: your-api-key" http://localhost:10000/health
```

### Analyze Blood Report (File Upload)
```bash
curl -X POST \
  -H "x-api-key: secret" \
  -F "file=@blood_report.pdf" \
  http://localhost:10000/analyze-report/
```

### Analyze Blood Report (JSON Data)
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: secret" \
  -d '{"hemoglobin": 12.5, "glucose": 95, "cholesterol": 180}' \
  http://localhost:10000/analyze-json/
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Using Docker directly
```bash
# Build the image
docker build -t inbloodo-agent .

# Run the container
docker run -d \
  -p 10000:10000 \
  -e API_KEY=your-secure-key \
  -v $(pwd)/data:/app/data \
  --name inbloodo-agent \
  inbloodo-agent
```

## ☁️ Cloud Deployment

### Render.com (Recommended)
1. Fork this repository
2. Connect to Render.com
3. Deploy using the included `render.yaml` configuration
4. Set environment variables in Render dashboard

### Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set API_KEY=your-secure-key
git push heroku main
```

### Railway
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:

```bash
ENVIRONMENT=production
HOST=0.0.0.0
PORT=10000
API_KEY=your-secure-api-key-here
DATABASE_URL=sqlite:///health_reports.db
LOG_LEVEL=INFO
```

### Supported File Formats
- **PDF**: Blood test reports in PDF format
- **CSV**: Structured data with parameter names and values
- **JSON**: Key-value pairs of medical parameters
- **Images**: PNG/JPG scanned reports (OCR processed)

## 💬 Conversational Examples

### Natural Language Queries
The AI can understand and respond to natural language queries:

- *"I'm feeling really tired lately, what could be wrong?"*
- *"Can you help me understand my cholesterol levels?"*
- *"I have high blood pressure, what should I do?"*
- *"Tell me about diabetes symptoms"*
- *"Upload my test results please"*

### Intent Inference Categories
The system automatically detects user intent:
- **analyze_blood_report**: Upload/analyze blood test results
- **ask_health_question**: General health inquiries
- **request_recommendations**: Seeking health advice
- **follow_up_previous_analysis**: Referring to previous results
- **clarify_previous_response**: Need clarification
- **general_health_inquiry**: Broad health information
- **emergency_concern**: Urgent health issues
- **lifestyle_advice**: Diet, exercise, wellness tips

### Clarification Handling
When the AI needs more information, it automatically asks relevant questions:
```
User: "My cholesterol is high"
AI: "I'd like to help better. Could you please clarify:
• What was your specific cholesterol reading?
• Do you have your full lipid panel results?
• Are you experiencing any symptoms?"
```

## 📊 Sample Data Format

### JSON Input Example
```json
{
  "hemoglobin": 12.5,
  "glucose": 95,
  "cholesterol": 180,
  "hdl": 45,
  "ldl": 120,
  "triglycerides": 150,
  "creatinine": 1.0,
  "urea": 25,
  "alt": 30,
  "ast": 25
}
```

### CSV Input Example
```csv
Parameter,Value,Unit
Hemoglobin,12.5,g/dL
Glucose,95,mg/dL
Cholesterol,180,mg/dL
HDL,45,mg/dL
LDL,120,mg/dL
```

## 🛡️ Security Features

- **API Key Authentication**: Secure access to all endpoints
- **Input Validation**: Comprehensive data validation and sanitization
- **Error Handling**: Graceful error handling with detailed logging
- **Rate Limiting**: Built-in protection against abuse
- **CORS Support**: Configurable cross-origin resource sharing

## 🔍 Health Monitoring

The application includes comprehensive health monitoring:

- **Health Check Endpoint**: `/health`
- **API Status**: `/api/status`
- **Database Connectivity**: Automatic database health checks
- **Logging**: Structured logging to files and console
- **Error Tracking**: Detailed error reporting and tracking

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run intent inference tests
python test_intent_inference.py

# Run with coverage
pytest --cov=src tests/
```

### Intent Inference Testing
Test the natural language understanding capabilities:
```bash
python test_intent_inference.py
```

This will test various user inputs and show:
- Inferred intent categories
- Confidence scores
- Clarifying questions generated
- Context awareness

### Manual Testing
Use the included test files in the `data/sample_report/` directory:
- `report.pdf` - Sample blood test report
- `test_report.png` - Sample image report

### Conversational Testing Examples
Try these natural language queries in the chat interface:
- *"I'm worried about my cholesterol levels"*
- *"Can you explain what high glucose means?"*
- *"I feel fatigued, could it be anemia?"*
- *"Upload and analyze my blood work"*

## 📈 Performance Optimization

- **Async Processing**: Non-blocking request handling
- **Connection Pooling**: Efficient database connections
- **Caching**: Intelligent caching of analysis results
- **Compression**: Response compression for faster loading
- **CDN Ready**: Static assets optimized for CDN delivery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and request features on GitHub Issues
- **Documentation**: Check the `/docs` endpoint when running in development mode
- **Health Check**: Monitor application status at `/health`

## 🔄 Updates

The application automatically handles:
- Database migrations
- Dependency updates
- Configuration changes
- Health monitoring

---

**⚠️ Medical Disclaimer**: This tool is for informational purposes only and should not replace professional medical advice. Always consult with qualified healthcare professionals for medical decisions.