"""Risk Scoring Engine: Multi-factor explainable risk calculation."""
from typing import List
from app.models.alert import Alert

ASSET_CRITICALITY = {
    "prod-db-server": 95,
    "domain-controller": 100,
    "win-workstation-01": 50,
    "ops-server-01": 40,
    "192.168.10.50": 95,
    "192.168.10.75": 50,
}

KNOWN_BAD_IPS = {"203.0.113.45", "198.51.100.99"}


def calculate_incident_risk(alerts: List[Alert], tactics: List[str], entity_key: str) -> dict:
    """Calculate explainable risk score. Returns {score, severity, confidence, factors}."""
    factors = []
    score = 0.0

    # Factor 1: Base Severity (0-35 pts)
    if alerts:
        avg_level = sum(a.rule_level for a in alerts) / len(alerts)
        max_level = max(a.rule_level for a in alerts)
        base_sev = ((avg_level * 0.4) + (max_level * 0.6)) / 15 * 35
        factors.append({
            "factor": "Alert Severity Level",
            "weight": round(base_sev, 1),
            "detail": f"Max rule level: {max_level}/15, avg: {avg_level:.1f}/15 across {len(alerts)} correlated alerts."
        })
        score += base_sev

    # Factor 2: Asset Criticality (0-25 pts)
    asset_raw = ASSET_CRITICALITY.get(entity_key, 30)
    asset_score = (asset_raw / 100) * 25
    label = "High-Value Asset" if asset_raw >= 70 else "Asset Criticality"
    factors.append({
        "factor": label,
        "weight": round(asset_score, 1),
        "detail": f"Target '{entity_key}' has criticality rating {asset_raw}/100."
    })
    score += asset_score

    # Factor 3: Attack Chain (0-25 pts)
    num_tactics = len(tactics)
    if num_tactics >= 3:
        chain_score = min(25, num_tactics * 5 + (10 if ("Exfiltration" in tactics or "Impact" in tactics) else 0))
        factors.append({
            "factor": "Multi-Stage Attack Chain Detected",
            "weight": round(chain_score, 1),
            "detail": f"Observed {num_tactics} distinct MITRE ATT&CK tactics: {', '.join(tactics)}. Sophisticated multi-stage campaign."
        })
    elif num_tactics >= 2:
        chain_score = num_tactics * 4
        factors.append({
            "factor": "Multi-Phase Attack Pattern",
            "weight": round(chain_score, 1),
            "detail": f"Observed {num_tactics} MITRE ATT&CK tactics: {', '.join(tactics)}."
        })
    elif num_tactics == 1:
        chain_score = 3.0
        factors.append({"factor": "Single-Phase Threat", "weight": 3.0, "detail": f"Single tactic: {tactics[0]}."})
    else:
        chain_score = 2.0
        factors.append({"factor": "Uncategorized Activity", "weight": 2.0, "detail": "No MITRE tactic mapping. Manual review recommended."})
    score += chain_score

    # Factor 4: Threat Context (0-15 pts)
    context_score = 0.0
    bad_ips = list({a.src_ip for a in alerts if a.src_ip and a.src_ip in KNOWN_BAD_IPS})
    if bad_ips:
        context_score += 10
        factors.append({"factor": "Known Malicious IP", "weight": 10.0, "detail": f"Source IP(s) {bad_ips} match threat intel indicators."})
    if len(alerts) >= 15:
        vol = min(5.0, len(alerts) * 0.2)
        context_score += vol
        factors.append({"factor": "High Alert Volume", "weight": round(vol, 1), "detail": f"{len(alerts)} alerts in window indicate automated/high-intensity activity."})
    score += min(15.0, context_score)

    final_score = min(100.0, score)
    if final_score >= 75:
        severity = "CRITICAL"
    elif final_score >= 55:
        severity = "HIGH"
    elif final_score >= 35:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    confidence = min(0.99, 0.5 + len(alerts) * 0.03 + num_tactics * 0.05)
    return {"score": round(final_score, 1), "severity": severity, "confidence": round(confidence, 2), "factors": factors}
