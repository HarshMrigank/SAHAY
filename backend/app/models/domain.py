from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    NGO = "ngo"
    RESPONDER = "responder"
    THERAPIST = "therapist"

class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class RegistrationRequest(Base):
    __tablename__ = "registration_requests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String) # RoleEnum
    organization = Column(String, nullable=True)
    status = Column(String, default=RequestStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, index=True)
    role = Column(String)
    organization = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cases = relationship("Case", back_populates="assigned_to_user")
    interventions = relationship("Intervention", back_populates="created_by_user")

class VictimProfile(Base):
    __tablename__ = "victim_profiles"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    contact_info = Column(String, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cases = relationship("Case", back_populates="victim")
    distress_scores = relationship("DistressScore", back_populates="victim")

class CaseStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default=CaseStatus.OPEN.value)
    victim_id = Column(Integer, ForeignKey("victim_profiles.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    victim = relationship("VictimProfile", back_populates="cases")
    assigned_to_user = relationship("User", back_populates="cases")
    assessments = relationship("Assessment", back_populates="case")
    alerts = relationship("Alert", back_populates="case")
    interventions = relationship("Intervention", back_populates="case")

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    assessment_data = Column(JSON)
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="assessments")

class DistressScore(Base):
    __tablename__ = "distress_scores"
    id = Column(Integer, primary_key=True, index=True)
    victim_id = Column(Integer, ForeignKey("victim_profiles.id"))
    score = Column(Float)
    factors = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    victim = relationship("VictimProfile", back_populates="distress_scores")

class AlertLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    level = Column(String, default=AlertLevel.LOW.value)
    message = Column(String)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="alerts")

class Intervention(Base):
    __tablename__ = "interventions"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    action_taken = Column(Text)
    outcome = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="interventions")
    created_by_user = relationship("User", back_populates="interventions")
