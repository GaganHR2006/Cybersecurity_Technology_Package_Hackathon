from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ActionApproval(BaseModel):
    analyst: str
    notes: Optional[str] = None

class ActionRejection(BaseModel):
    analyst: str
    reason: str

class ActionResponse(BaseModel):
    action_id: str
    incident_id: str
    name: str
    description: str
    target: str
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
