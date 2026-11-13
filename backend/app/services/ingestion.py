"""Ingestion Service: Parses and normalizes incoming alert payloads."""
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.audit import AuditLog
from app.schemas.alert import AlertIngest


def ingest_alert(alert_data: AlertIngest, db: Session) -> Alert:
    """Persist an incoming normalized alert. Returns existing if duplicate alert_id."""
    existing = db.query(Alert).filter(Alert.alert_id == alert_data.alert_id).first()
    if existing:
        return existing

    alert = Alert(
        alert_id=alert_data.alert_id,
        source=alert_data.source,
        timestamp=alert_data.timestamp,
        agent_id=alert_data.agent.id,
        agent_name=alert_data.agent.name,
        agent_ip=alert_data.agent.ip,
        rule_id=alert_data.rule.id,
        rule_level=alert_data.rule.level,
        rule_description=alert_data.rule.description,
        mitre_id=alert_data.rule.mitre.id,
        mitre_tactic=alert_data.rule.mitre.tactic,
        mitre_technique=alert_data.rule.mitre.technique,
        src_ip=alert_data.data.src_ip,
        dst_port=alert_data.data.dst_port,
        user=alert_data.data.user,
        raw_log=alert_data.raw_log,
        raw_data=alert_data.model_dump(mode="json"),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    db.add(AuditLog(
        event_type="ALERT_INGESTED",
        detail=f"Alert {alert.alert_id} ingested from {alert.source} for agent {alert.agent_name}"
    ))
    db.commit()
    return alert
