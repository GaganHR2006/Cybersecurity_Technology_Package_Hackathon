"""Threat Intelligence Service: MITRE ATT&CK mappings, asset criticality, CVE data."""
from typing import Optional, List

TACTIC_ORDER = {
    "Reconnaissance": 1, "Resource Development": 2, "Initial Access": 3,
    "Execution": 4, "Persistence": 5, "Privilege Escalation": 6,
    "Defense Evasion": 7, "Credential Access": 8, "Discovery": 9,
    "Lateral Movement": 10, "Collection": 11, "Command and Control": 12,
    "Exfiltration": 13, "Impact": 14,
}

WAZUH_RULE_TO_MITRE = {
    "5503": {"technique_id": "T1110", "technique_name": "Brute Force", "tactic": "Credential Access", "severity_boost": 1.2},
    "5501": {"technique_id": "T1078", "technique_name": "Valid Accounts", "tactic": "Initial Access", "severity_boost": 1.5},
    "5712": {"technique_id": "T1021", "technique_name": "Remote Services", "tactic": "Lateral Movement", "severity_boost": 1.3},
    "5902": {"technique_id": "T1005", "technique_name": "Data from Local System", "tactic": "Collection", "severity_boost": 1.4},
    "5903": {"technique_id": "T1486", "technique_name": "Data Encrypted for Impact", "tactic": "Impact", "severity_boost": 2.0},
    "92201": {"technique_id": "T1059.001", "technique_name": "PowerShell", "tactic": "Execution", "severity_boost": 1.6},
    "92300": {"technique_id": "T1490", "technique_name": "Inhibit System Recovery", "tactic": "Impact", "severity_boost": 2.5},
    "suricata-et-policy-001": {"technique_id": "T1048", "technique_name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration", "severity_boost": 1.8},
}

ASSET_CRITICALITY_DB = {
    "prod-db-server": {"score": 95, "label": "Critical Data Store", "tags": ["database", "pii", "production"]},
    "win-workstation-01": {"score": 50, "label": "Standard Workstation", "tags": ["endpoint", "user"]},
    "ops-server-01": {"score": 40, "label": "Operations Server", "tags": ["internal", "admin"]},
    "domain-controller": {"score": 100, "label": "Domain Controller", "tags": ["active-directory", "critical", "identity"]},
    "192.168.10.50": {"score": 95, "label": "Critical Data Store", "tags": ["database", "pii", "production"]},
    "192.168.10.75": {"score": 50, "label": "Standard Workstation", "tags": ["endpoint", "user"]},
}

KNOWN_BAD_IPS = {
    "203.0.113.45": {"reputation": "malicious", "category": "scanner", "confidence": 0.9},
    "198.51.100.99": {"reputation": "suspicious", "category": "tor_exit_node", "confidence": 0.7},
}

CVE_INVENTORY = {
    "prod-db-server": [
        {"cve": "CVE-2024-1234", "severity": "HIGH", "cvss": 8.5, "description": "OpenSSH authentication bypass", "patched": False},
        {"cve": "CVE-2023-5678", "severity": "MEDIUM", "cvss": 6.5, "description": "sudo privilege escalation", "patched": True},
    ],
    "win-workstation-01": [
        {"cve": "CVE-2024-5555", "severity": "CRITICAL", "cvss": 9.8, "description": "Windows SMB remote code execution", "patched": False},
    ],
}


def get_mitre_info(rule_id: str) -> Optional[dict]:
    return WAZUH_RULE_TO_MITRE.get(rule_id)


def get_asset_criticality(hostname_or_ip: str) -> dict:
    return ASSET_CRITICALITY_DB.get(hostname_or_ip, {"score": 30, "label": "Unknown Asset", "tags": []})


def get_ip_reputation(ip: str) -> Optional[dict]:
    return KNOWN_BAD_IPS.get(ip)


def get_host_cves(hostname: str) -> List[dict]:
    return [c for c in CVE_INVENTORY.get(hostname, []) if not c.get("patched", True)]


def get_tactic_severity_order(tactic: str) -> int:
    return TACTIC_ORDER.get(tactic, 0)


def calculate_attack_chain_score(tactics: List[str]) -> float:
    if not tactics:
        return 0.0
    orders = [TACTIC_ORDER.get(t, 0) for t in tactics]
    max_order = max(orders) if orders else 0
    coverage = len(set(tactics)) / len(TACTIC_ORDER)
    late_stage_bonus = 0.3 if max_order >= 11 else 0.0
    score = min(1.0, (coverage * 0.5) + (max_order / len(TACTIC_ORDER) * 0.5) + late_stage_bonus)
    return round(score, 2)


def enrich_alert_with_threat_intel(alert: dict) -> dict:
    enriched = dict(alert)
    rule_id = alert.get("rule", {}).get("id", "")
    enriched["mitre_info"] = get_mitre_info(rule_id)
    agent_name = alert.get("agent", {}).get("name", "")
    agent_ip = alert.get("agent", {}).get("ip", "")
    enriched["asset_criticality"] = get_asset_criticality(agent_name) or get_asset_criticality(agent_ip)
    src_ip = alert.get("data", {}).get("src_ip", "")
    enriched["ip_reputation"] = get_ip_reputation(src_ip) if src_ip else None
    enriched["relevant_cves"] = get_host_cves(agent_name)
    return enriched
