from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, func
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, default="OPEN")
    severity = Column(String)
    risk_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    primary_entity_type = Column(String)
    primary_entity_id = Column(String, index=True)
    primary_entity_ip = Column(String)
    risk_factors = Column(JSON)
    attack_timeline = Column(JSON)
    recommended_actions = Column(JSON)
    alert_ids = Column(JSON)
    tactics_observed = Column(JSON)
    techniques_observed = Column(JSON)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    analyst_notes = Column(String, nullable=True)
