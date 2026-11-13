from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.incident import Incident
from app.models.audit import AuditLog
from app.schemas.incident import IncidentResponse, IncidentSummary, IncidentStatusUpdate, RiskFactor, TimelineStep, RecommendedAction

router = APIRouter(prefix="/incidents", tags=["Incidents"])

def _to_response(inc: Incident) -> IncidentResponse:
    return IncidentResponse(
        incident_id=inc.incident_id, title=inc.title, status=inc.status,
        severity=inc.severity or "LOW", risk_score=inc.risk_score or 0.0,
        confidence=inc.confidence or 0.0, primary_entity_type=inc.primary_entity_type,
        primary_entity_id=inc.primary_entity_id, primary_entity_ip=inc.primary_entity_ip,
        risk_factors=[RiskFactor(**f) for f in (inc.risk_factors or [])],
        attack_timeline=[TimelineStep(**t) for t in (inc.attack_timeline or [])],
        recommended_actions=[RecommendedAction(**a) for a in (inc.recommended_actions or [])],
        alert_ids=inc.alert_ids or [], tactics_observed=inc.tactics_observed or [],
        first_seen=inc.first_seen, last_seen=inc.last_seen, created_at=inc.created_at,
        analyst_notes=inc.analyst_notes
    )

@router.get("/", response_model=List[IncidentSummary])
def list_incidents(status: Optional[str] = None, severity: Optional[str] = None,
                   skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(Incident)
    if status:
        q = q.filter(Incident.status == status.upper())
    if severity:
        q = q.filter(Incident.severity == severity.upper())
    incidents = q.order_by(Incident.risk_score.desc()).offset(skip).limit(limit).all()
    return [IncidentSummary(
        incident_id=i.incident_id, title=i.title, status=i.status,
        severity=i.severity or "LOW", risk_score=i.risk_score or 0.0,
        primary_entity_id=i.primary_entity_id, alert_count=len(i.alert_ids or []),
        first_seen=i.first_seen, last_seen=i.last_seen, created_at=i.created_at
    ) for i in incidents]

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not inc:
        raise HTTPException(404, f"Incident {incident_id} not found")
    return _to_response(inc)

@router.patch("/{incident_id}/status", response_model=IncidentResponse)
def update_status(incident_id: str, update: IncidentStatusUpdate, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not inc:
        raise HTTPException(404, f"Incident {incident_id} not found")
    valid = {"OPEN","UNDER_REVIEW","CONTAINED","RESOLVED","FALSE_POSITIVE"}
    if update.status.upper() not in valid:
        raise HTTPException(400, f"Invalid status. Must be one of: {valid}")
    old = inc.status
    inc.status = update.status.upper()
    if update.analyst_notes:
        inc.analyst_notes = update.analyst_notes
    db.add(AuditLog(event_type="INCIDENT_STATUS_CHANGED", incident_id=incident_id,
        analyst=update.analyst, detail=f"Status: {old} -> {inc.status}. Notes: {update.analyst_notes or 'None'}"))
    db.commit()
    db.refresh(inc)
    return _to_response(inc)
