from sqlalchemy import Column, String, Integer, DateTime, func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    incident_id = Column(String, index=True, nullable=True)
    action_id = Column(String, nullable=True)
    analyst = Column(String, nullable=True)
    detail = Column(String)
    created_at = Column(DateTime, server_default=func.now())
