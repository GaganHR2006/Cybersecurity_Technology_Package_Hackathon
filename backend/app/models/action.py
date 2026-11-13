from sqlalchemy import Column, String, Integer, DateTime, Boolean, func
from app.core.database import Base

class ResponseAction(Base):
    __tablename__ = "response_actions"
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String, unique=True, index=True)
    incident_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    target = Column(String)
    status = Column(String, default="PENDING_APPROVAL")
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
