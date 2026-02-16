# Quick reference for new API endpoints

## Health Score Endpoint
GET /api/health-score
Returns: {
  "overall_score": 85,
  "category_scores": {
    "metabolic": 90,
    "cardiovascular": 80,
    "liver": 85,
    "kidney": 88
  },
  "trend": "improving",
  "last_updated": "2026-02-16T18:51:00Z"
}

## Alerts Endpoint
GET /api/alerts
Returns: {
  "critical": [
    {"parameter": "Glucose", "value": 180, "normal_range": "70-100", "severity": "high"}
  ],
  "warnings": [
    {"parameter": "Cholesterol", "value": 210, "normal_range": "<200", "severity": "moderate"}
  ]
}

## Health Tips Endpoint
GET /api/health-tips
Returns: {
  "tips": [
    "🥗 Increase fiber intake to help lower cholesterol",
    "🏃 30 minutes of daily exercise can improve glucose control",
    "💧 Stay hydrated with 8 glasses of water daily"
  ],
  "personalized": true,
  "based_on_report_id": 100
}
