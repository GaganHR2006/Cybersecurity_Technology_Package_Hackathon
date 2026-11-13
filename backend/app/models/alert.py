from sqlalchemy import Column, String, Integer, DateTime, JSON, func
from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    agent_id = Column(String, index=True)
    agent_name = Column(String, index=True)
    agent_ip = Column(String, index=True)
    rule_id = Column(String, index=True)
    rule_level = Column(Integer)
    rule_description = Column(String)
    mitre_id = Column(JSON)
    mitre_tactic = Column(JSON)
    mitre_technique = Column(JSON)
    src_ip = Column(String, index=True)
    dst_port = Column(Integer)
    user = Column(String, index=True)
    raw_log = Column(String)
    raw_data = Column(JSON)
    incident_id = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
