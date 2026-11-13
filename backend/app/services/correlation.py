"""Correlation Engine: Groups alerts into incidents via sliding-window entity matching."""
import uuid
from datetime import timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.audit import AuditLog
from app.core.config import settings


def _entity_keys(alert: Alert) -> List[str]:
    keys = []
    if alert.agent_name:
        keys.append(f"host:{alert.agent_name}")
    if alert.agent_ip:
        keys.append(f"ip:{alert.agent_ip}")
    if alert.user and alert.user not in ("root", "system", "SYSTEM"):
        keys.append(f"user:{alert.user}")
    if alert.src_ip:
        keys.append(f"src_ip:{alert.src_ip}")
    return keys


def _generate_title(alerts: List[Alert], tactics: List[str]) -> str:
    name = alerts[0].agent_name or alerts[0].agent_ip or "Unknown Host"
    if len(tactics) >= 3:
        return f"Multi-Stage Attack Campaign Detected on {name}"
    if "Exfiltration" in tactics:
        return f"Suspected Data Exfiltration from {name}"
    if "Impact" in tactics:
        return f"Destructive Activity Detected on {name}"
    if "Credential Access" in tactics or "Initial Access" in tactics:
        user = alerts[0].user
        return f"Credential Compromise — {user} on {name}" if user else f"Unauthorized Access Attempt on {name}"
    return f"Suspicious Activity Cluster on {name}"


def _build_recommended_actions(incident_id: str, first_alert: Alert, severity: str) -> List[dict]:
    actions = []
    if severity in ("CRITICAL", "HIGH"):
        actions.append({
            "action_id": f"ACT-ISO-{str(uuid.uuid4())[:4].upper()}",
            "name": "Isolate Endpoint",
            "description": f"Drop all network connections on {first_alert.agent_name} except management.",
            "requires_approval": True,
            "target": f"{first_alert.agent_name} ({first_alert.agent_ip})",
            "status": "PENDING_APPROVAL"
        })
    if first_alert.user and severity in ("CRITICAL", "HIGH", "MEDIUM"):
        actions.append({
            "action_id": f"ACT-REV-{str(uuid.uuid4())[:4].upper()}",
            "name": "Revoke User Session & Disable Account",
            "description": f"Kill active sessions and temporarily disable {first_alert.user}.",
            "requires_approval": True,
            "target": first_alert.user,
            "status": "PENDING_APPROVAL"
        })
    actions.append({
        "action_id": f"ACT-INV-{str(uuid.uuid4())[:4].upper()}",
        "name": "Begin Forensic Investigation",
        "description": "Collect memory dump and disk image from affected host.",
        "requires_approval": True,
        "target": f"{first_alert.agent_name} ({first_alert.agent_ip})",
        "status": "PENDING_APPROVAL"
    })
    return actions


def _create_incident(alerts: List[Alert], db: Session) -> Incident:
    from app.services.risk_scorer import calculate_incident_risk
    alerts_sorted = sorted(alerts, key=lambda a: a.timestamp)
    first = alerts_sorted[0]
    last = alerts_sorted[-1]

    entity_id = first.agent_name or first.agent_ip or "unknown"
    if first.user:
        entity_id = f"{first.agent_name}::{first.user}"

    all_tactics = []
    all_techniques = []
    for a in alerts:
        if a.mitre_tactic:
            all_tactics.extend(a.mitre_tactic)
        if a.mitre_technique:
            all_techniques.extend(a.mitre_technique)
    unique_tactics = list(dict.fromkeys(all_tactics))
    unique_techniques = list(dict.fromkeys(all_techniques))

    incident_id = f"INC-{last.timestamp.strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}"

    timeline = []
    for i, a in enumerate(alerts_sorted):
        tactic_str = (a.mitre_tactic[0] if a.mitre_tactic else "Unknown")
        tech_str = (a.mitre_technique[0] if a.mitre_technique else a.rule_description)
        timeline.append({
            "step": i + 1,
            "stage": f"{tactic_str} / {tech_str}",
            "timestamp": a.timestamp.isoformat(),
            "alert_id": a.alert_id,
            "summary": a.rule_description
        })

    risk = calculate_incident_risk(alerts, unique_tactics, first.agent_name or first.agent_ip or "")
    title = _generate_title(alerts_sorted, unique_tactics)
    rec_actions = _build_recommended_actions(incident_id, first, risk["severity"])

    incident = Incident(
        incident_id=incident_id,
        title=title,
        status="OPEN",
        severity=risk["severity"],
        risk_score=risk["score"],
        confidence=risk["confidence"],
        primary_entity_type="HOST_AND_USER" if "::" in entity_id else "HOST",
        primary_entity_id=entity_id,
        primary_entity_ip=first.agent_ip,
        risk_factors=risk["factors"],
        attack_timeline=timeline,
        recommended_actions=rec_actions,
        alert_ids=[a.alert_id for a in alerts],
        tactics_observed=unique_tactics,
        techniques_observed=unique_techniques,
        first_seen=first.timestamp,
        last_seen=last.timestamp,
    )
    db.add(incident)
    for a in alerts:
        a.incident_id = incident_id
    db.commit()
    db.refresh(incident)

    db.add(AuditLog(
        event_type="INCIDENT_CREATED",
        incident_id=incident_id,
        detail=f"Incident created with {len(alerts)} alerts. Score: {risk['score']}. Severity: {risk['severity']}"
    ))
    db.commit()
    return incident


def _add_to_incident(incident: Incident, alert: Alert, db: Session):
    from app.services.risk_scorer import calculate_incident_risk
    ids = list(incident.alert_ids or [])
    if alert.alert_id not in ids:
        ids.append(alert.alert_id)
        incident.alert_ids = ids

    tactic_str = (alert.mitre_tactic[0] if alert.mitre_tactic else "Unknown")
    tech_str = (alert.mitre_technique[0] if alert.mitre_technique else alert.rule_description)
    timeline = list(incident.attack_timeline or [])
    timeline.append({
        "step": len(timeline) + 1,
        "stage": f"{tactic_str} / {tech_str}",
        "timestamp": alert.timestamp.isoformat(),
        "alert_id": alert.alert_id,
        "summary": alert.rule_description
    })
    incident.attack_timeline = timeline

    tactics = list(incident.tactics_observed or [])
    if alert.mitre_tactic:
        for t in alert.mitre_tactic:
            if t not in tactics:
                tactics.append(t)
    incident.tactics_observed = tactics

    if alert.timestamp > incident.last_seen:
        incident.last_seen = alert.timestamp

    all_alerts = db.query(Alert).filter(Alert.incident_id == incident.incident_id).all()
    risk = calculate_incident_risk(all_alerts + [alert], tactics, incident.primary_entity_ip or "")
    incident.risk_score = risk["score"]
    incident.severity = risk["severity"]
    incident.confidence = risk["confidence"]
    incident.risk_factors = risk["factors"]

    alert.incident_id = incident.incident_id
    db.commit()


def correlate_alert(alert: Alert, db: Session) -> Optional[str]:
    """Attempt to correlate alert into existing or new incident. Returns incident_id or None."""
    window_start = alert.timestamp - timedelta(minutes=settings.CORRELATION_WINDOW_MINUTES)
    window_end = alert.timestamp + timedelta(minutes=settings.CORRELATION_WINDOW_MINUTES)

    nearby = db.query(Alert).filter(
        Alert.timestamp >= window_start,
        Alert.timestamp <= window_end,
        Alert.id != alert.id
    ).all()

    my_keys = set(_entity_keys(alert))
    related = [a for a in nearby if my_keys.intersection(set(_entity_keys(a)))]

    if not related:
        return None

    # Look for existing incident among related alerts
    incident_id = None
    for r in related:
        if r.incident_id:
            incident_id = r.incident_id
            break

    if incident_id:
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if incident:
            _add_to_incident(incident, alert, db)
            return incident_id
    else:
        unincidented = [a for a in related if not a.incident_id]
        if len(unincidented) >= settings.MIN_ALERTS_FOR_INCIDENT - 1:
            new_incident = _create_incident(unincidented + [alert], db)
            return new_incident.incident_id

    return None
