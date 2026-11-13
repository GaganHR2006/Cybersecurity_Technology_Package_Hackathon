from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.action import ResponseAction
from app.models.audit import AuditLog
from app.schemas.risk import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    total_alerts = db.query(Alert).count()
    total_inc = db.query(Incident).count()
    return MetricsResponse(
        total_alerts_ingested=total_alerts,
        total_incidents_created=total_inc,
        open_incidents=db.query(Incident).filter(Incident.status == "OPEN").count(),
        critical_incidents=db.query(Incident).filter(Incident.severity == "CRITICAL").count(),
        high_incidents=db.query(Incident).filter(Incident.severity == "HIGH").count(),
        medium_incidents=db.query(Incident).filter(Incident.severity == "MEDIUM").count(),
        low_incidents=db.query(Incident).filter(Incident.severity == "LOW").count(),
        false_positive_count=db.query(Incident).filter(Incident.status == "FALSE_POSITIVE").count(),
        false_positive_rate=round(
            db.query(Incident).filter(Incident.status == "FALSE_POSITIVE").count() / total_inc * 100
            if total_inc > 0 else 0.0, 2),
        avg_alerts_per_incident=round(total_alerts / total_inc if total_inc > 0 else 0.0, 1),
        total_response_actions=db.query(ResponseAction).count(),
        pending_approvals=db.query(ResponseAction).filter(ResponseAction.status == "PENDING_APPROVAL").count(),
    )

@router.get("/audit-log")
def get_audit_log(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return [{"id": l.id, "event_type": l.event_type, "incident_id": l.incident_id,
             "action_id": l.action_id, "analyst": l.analyst, "detail": l.detail,
             "created_at": l.created_at} for l in logs]
