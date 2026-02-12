from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

# Use environment variable for database URL
# Use environment variable for database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///health_reports.db")

# Fix for Render/Heroku 'postgres://' schema which is deprecated in SQLAlchemy 1.4+
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure connection args based on database type
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

# Production-grade engine configuration
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    connect_args=connect_args,
    # Best practices for production resilience:
    pool_pre_ping=True,  # Checks connection before using it (prevents stale connection errors)
    pool_size=10,        # Sensible default for pool size
    max_overflow=20,     # Allow some burst
    pool_recycle=300     # Recycle connections every 5 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default="patient")  # admin, doctor, patient
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)  # google, facebook, github, microsoft
    oauth_provider_id = Column(String(100), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Report(Base):
    """Blood report analysis model"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to user
    filename = Column(String, index=True)
    parameters = Column(Text)  # JSON string
    precautions = Column(Text)  # JSON string
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, filename='{self.filename}', user_id={self.user_id})>"


# Create tables
Base.metadata.create_all(bind=engine)