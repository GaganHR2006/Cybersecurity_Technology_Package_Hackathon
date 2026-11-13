from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class RiskFactor(BaseModel):
    factor: str
    weight: float
    detail: str

class TimelineStep(BaseModel):
    step: int
    stage: str
    timestamp: datetime
    alert_id: str
    summary: str

class RecommendedAction(BaseModel):
    action_id: str
    name: str
    description: str
    requires_approval: bool = True
    target: str
    status: str = "PENDING_APPROVAL"

class IncidentResponse(BaseModel):
    incident_id: str
    title: str
    status: str
    severity: str
    risk_score: float
    confidence: float
    primary_entity_type: Optional[str] = None
    primary_entity_id: Optional[str] = None
    primary_entity_ip: Optional[str] = None
    risk_factors: List[RiskFactor] = []
    attack_timeline: List[TimelineStep] = []
    recommended_actions: List[RecommendedAction] = []
    alert_ids: List[str] = []
    tactics_observed: List[str] = []
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    analyst_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class IncidentSummary(BaseModel):
    incident_id: str
    title: str
    status: str
    severity: str
    risk_score: float
    primary_entity_id: Optional[str] = None
    alert_count: int
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime

class IncidentStatusUpdate(BaseModel):
    status: str
    analyst_notes: Optional[str] = None
    analyst: str = "analyst"
