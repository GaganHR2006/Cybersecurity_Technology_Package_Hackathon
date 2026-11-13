import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.services.response_manager import approve_action, reject_action

def make_db_with_action(status="PENDING_APPROVAL"):
    action = MagicMock()
    action.action_id = "ACT-TEST-0001"
    action.incident_id = "INC-TEST-001"
    action.name = "Isolate Endpoint"
    action.target = "test-host"
    action.status = status
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = action
    return db, action

def test_approve_action_sets_executed():
    db, action = make_db_with_action()
    result = approve_action("ACT-TEST-0001", "analyst1", "looks good", db)
    assert action.status == "EXECUTED"
    assert action.approved_by == "analyst1"
    db.commit.assert_called()

def test_reject_action_sets_rejected():
    db, action = make_db_with_action()
    result = reject_action("ACT-TEST-0001", "analyst1", "false positive suspected", db)
    assert action.status == "REJECTED"
    assert action.rejection_reason == "false positive suspected"

def test_approve_already_executed_raises():
    db, action = make_db_with_action(status="EXECUTED")
    with pytest.raises(ValueError, match="not pending"):
        approve_action("ACT-TEST-0001", "analyst1", None, db)

def test_reject_missing_action_raises():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ValueError, match="not found"):
        reject_action("NONEXISTENT", "analyst1", "reason", db)
