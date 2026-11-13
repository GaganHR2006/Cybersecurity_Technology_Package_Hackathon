"""Response Manager: Human-in-the-loop approval workflow."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.action import ResponseAction
from app.models.audit import AuditLog


def approve_action(action_id: str, analyst: str, notes: Optional[str], db: Session) -> ResponseAction:
    action = db.query(ResponseAction).filter(ResponseAction.action_id == action_id).first()
    if not action:
        raise ValueError(f"Action {action_id} not found")
    if action.status != "PENDING_APPROVAL":
        raise ValueError(f"Action {action_id} is not pending (status: {action.status})")
    action.status = "EXECUTED"
    action.approved_by = analyst
    action.approved_at = datetime.utcnow()
    action.executed_at = datetime.utcnow()
    db.add(AuditLog(
        event_type="ACTION_APPROVED_AND_EXECUTED",
        incident_id=action.incident_id,
        action_id=action_id,
        analyst=analyst,
        detail=f"'{action.name}' approved by {analyst} and executed on {action.target}. Notes: {notes or 'None'}"
    ))
    db.commit()
    db.refresh(action)
    return action


def reject_action(action_id: str, analyst: str, reason: str, db: Session) -> ResponseAction:
    action = db.query(ResponseAction).filter(ResponseAction.action_id == action_id).first()
    if not action:
        raise ValueError(f"Action {action_id} not found")
    if action.status != "PENDING_APPROVAL":
        raise ValueError(f"Action {action_id} is not pending (status: {action.status})")
    action.status = "REJECTED"
    action.approved_by = analyst
    action.approved_at = datetime.utcnow()
    action.rejection_reason = reason
    db.add(AuditLog(
        event_type="ACTION_REJECTED",
        incident_id=action.incident_id,
        action_id=action_id,
        analyst=analyst,
        detail=f"'{action.name}' REJECTED by {analyst}. Reason: {reason}"
    ))
    db.commit()
    db.refresh(action)
    return action


def create_response_actions_from_recommendations(incident_id: str, recommendations: list, db: Session):
    for rec in recommendations:
        exists = db.query(ResponseAction).filter(ResponseAction.action_id == rec["action_id"]).first()
        if not exists:
            db.add(ResponseAction(
                action_id=rec["action_id"],
                incident_id=incident_id,
                name=rec["name"],
                description=rec["description"],
                target=rec["target"],
                requires_approval=rec.get("requires_approval", True),
                status="PENDING_APPROVAL"
            ))
    db.commit()
