from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class BloodParameter(BaseModel):
    """Individual blood test parameter"""
    name: str
    value: float
    unit: str
    reference_range: Optional[str] = None
    reference_min: Optional[float] = None
    reference_max: Optional[float] = None
    status: Optional[str] = None  # normal, high, low, borderline
    
    model_config = ConfigDict(from_attributes=True)

class UserContextInput(BaseModel):
    """User context for personalized analysis"""
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    medical_conditions: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    lifestyle_factors: Optional[Dict[str, Any]] = None

class ReportUploadResponse(BaseModel):
    """Response after uploading a report"""
    report_id: int
    filename: str
    status: ReportStatus
    message: str

class ParameterInterpretation(BaseModel):
    """Model 1 output"""
    parameter: str
    status: str  # normal, high, low, borderline
    severity: str  # mild, moderate, severe
    clinical_significance: str
    confidence: float

class PatternRecognition(BaseModel):
    """Model 2 output"""
    pattern_name: str
    description: str
    affected_parameters: List[str]
    risk_level: str  # low, moderate, high
    confidence: float

class RiskScore(BaseModel):
    """Risk assessment"""
    risk_type: str  # cardiovascular, diabetes, kidney, etc.
    score: float
    category: str  # low, moderate, high
    explanation: str

class Recommendation(BaseModel):
    """Health recommendation"""
    category: str  # diet, lifestyle, medical_followup
    title: str
    description: str
    priority: str  # low, medium, high
    related_findings: List[str]

class ReportAnalysisResponse(BaseModel):
    """Complete analysis response"""
    report_id: int
    status: ReportStatus
    
    # Extracted data
    parameters: List[BloodParameter]
    
    # Analysis results
    interpretations: List[ParameterInterpretation]
    patterns: List[PatternRecognition]
    risk_scores: List[RiskScore]
    
    # Recommendations
    recommendations: List[Recommendation]
    
    # Summary
    summary: str
    
    # Confidence
    overall_confidence: float
    
    # Disclaimer
    disclaimer: str
    
    # Timestamps
    processed_at: Optional[datetime] = None
