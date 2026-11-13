from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.action import ResponseAction
from app.schemas.response import ActionApproval, ActionRejection, ActionResponse
from app.services.response_manager import approve_action, reject_action

router = APIRouter(prefix="/responses", tags=["Responses"])

def _to_resp(a: ResponseAction) -> ActionResponse:
    return ActionResponse(action_id=a.action_id, incident_id=a.incident_id, name=a.name,
        description=a.description, target=a.target, status=a.status,
        approved_by=a.approved_by, approved_at=a.approved_at,
        rejection_reason=a.rejection_reason, created_at=a.created_at)

@router.get("/incident/{incident_id}", response_model=List[ActionResponse])
def get_actions(incident_id: str, db: Session = Depends(get_db)):
    return [_to_resp(a) for a in db.query(ResponseAction).filter(ResponseAction.incident_id == incident_id).all()]

@router.post("/{action_id}/approve", response_model=ActionResponse)
def approve(action_id: str, body: ActionApproval, db: Session = Depends(get_db)):
    try:
        return _to_resp(approve_action(action_id, body.analyst, body.notes, db))
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/{action_id}/reject", response_model=ActionResponse)
def reject(action_id: str, body: ActionRejection, db: Session = Depends(get_db)):
    try:
        return _to_resp(reject_action(action_id, body.analyst, body.reason, db))
    except ValueError as e:
        raise HTTPException(400, str(e))
