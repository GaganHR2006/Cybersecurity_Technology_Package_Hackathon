import pytest
from unittest.mock import MagicMock
from app.services.risk_scorer import calculate_incident_risk

def make_alert(rule_level, mitre_tactic=None, mitre_technique=None, src_ip=None, agent_name="test-host"):
    a = MagicMock()
    a.rule_level = rule_level
    a.mitre_tactic = mitre_tactic or []
    a.mitre_technique = mitre_technique or []
    a.src_ip = src_ip
    a.agent_name = agent_name
    return a

def test_low_severity_single_alert():
    alerts = [make_alert(3)]
    result = calculate_incident_risk(alerts, [], "unknown-host")
    assert result["score"] < 35
    assert result["severity"] == "LOW"

def test_critical_multistage_attack():
    tactics = ["Credential Access", "Initial Access", "Collection", "Exfiltration"]
    alerts = [make_alert(12) for _ in range(18)]
    result = calculate_incident_risk(alerts, tactics, "prod-db-server")
    assert result["score"] >= 75
    assert result["severity"] == "CRITICAL"

def test_known_bad_ip_boosts_score():
    alerts_no_bad = [make_alert(8)]
    alerts_bad = [make_alert(8, src_ip="203.0.113.45")]
    r1 = calculate_incident_risk(alerts_no_bad, ["Credential Access"], "prod-db-server")
    r2 = calculate_incident_risk(alerts_bad, ["Credential Access"], "prod-db-server")
    assert r2["score"] > r1["score"]

def test_factors_always_returned():
    alerts = [make_alert(5)]
    result = calculate_incident_risk(alerts, ["Execution"], "win-workstation-01")
    assert len(result["factors"]) > 0
    for f in result["factors"]:
        assert "factor" in f
        assert "weight" in f
        assert "detail" in f
