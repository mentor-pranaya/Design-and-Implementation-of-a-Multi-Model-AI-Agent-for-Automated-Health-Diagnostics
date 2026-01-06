from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Float, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .database import Base

class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class BloodReport(Base):
    """Blood report model"""
    __tablename__ = "blood_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)  # For future user management
    
    # File information
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, image, json
    file_path = Column(String, nullable=False)
    
    # Processing status
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Extracted data
    extracted_parameters = Column(JSON, nullable=True)  # Raw extracted data
    validated_parameters = Column(JSON, nullable=True)  # Cleaned and validated data
    
    # Analysis results
    model_1_results = Column(JSON, nullable=True)  # Parameter interpretation
    model_2_results = Column(JSON, nullable=True)  # Pattern recognition
    model_3_results = Column(JSON, nullable=True)  # Contextual analysis
    
    # Final output
    synthesized_findings = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    risk_scores = Column(JSON, nullable=True)
    
    # Confidence scores
    extraction_confidence = Column(Float, nullable=True)
    analysis_confidence = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<BloodReport(id={self.id}, filename={self.filename}, status={self.status})>"

class UserContext(Base):
    """User context for personalized analysis"""
    __tablename__ = "user_contexts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    
    # Demographics
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    
    # Medical history
    medical_conditions = Column(JSON, nullable=True)  # List of conditions
    medications = Column(JSON, nullable=True)  # Current medications
    allergies = Column(JSON, nullable=True)
    
    # Lifestyle
    lifestyle_factors = Column(JSON, nullable=True)  # Diet, exercise, smoking, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
