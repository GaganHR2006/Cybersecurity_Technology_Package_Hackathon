from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.alert import AlertIngest, AlertResponse
from app.services.ingestion import ingest_alert
from app.services.correlation import correlate_alert
from app.services.response_manager import create_response_actions_from_recommendations
from app.models.incident import Incident
from app.models.alert import Alert
from typing import List, Optional

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.post("/ingest", response_model=AlertResponse, status_code=201)
def ingest(alert_data: AlertIngest, db: Session = Depends(get_db)):
    alert = ingest_alert(alert_data, db)
    incident_id = correlate_alert(alert, db)
    if incident_id:
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if incident and incident.recommended_actions:
            create_response_actions_from_recommendations(incident_id, incident.recommended_actions, db)
    db.refresh(alert)
    return AlertResponse(
        alert_id=alert.alert_id, source=alert.source, timestamp=alert.timestamp,
        agent_name=alert.agent_name, rule_id=alert.rule_id, rule_level=alert.rule_level,
        rule_description=alert.rule_description, incident_id=alert.incident_id, created_at=alert.created_at
    )

@router.get("/", response_model=List[AlertResponse])
def list_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).offset(skip).limit(limit).all()
    return [AlertResponse(
        alert_id=a.alert_id, source=a.source, timestamp=a.timestamp,
        agent_name=a.agent_name, rule_id=a.rule_id, rule_level=a.rule_level,
        rule_description=a.rule_description, incident_id=a.incident_id, created_at=a.created_at
    ) for a in alerts]
