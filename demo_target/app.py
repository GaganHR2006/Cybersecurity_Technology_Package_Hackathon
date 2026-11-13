#!/usr/bin/env python3
"""
AcmeCorp Employee Portal — DEMO TARGET
This is a realistic fake company login page used to demonstrate
how CyberWatch detects brute-force attacks in real-time.

Credentials (intentionally weak for demo):
  admin / password123   ← will be found by attacker
  ceo   / Acme@2024     ← harder password
"""
import os
import uuid
import threading
from datetime import datetime, timezone
from collections import defaultdict
from flask import Flask, request, render_template, redirect, url_for, session, jsonify

try:
    import requests as req_lib
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

app = Flask(__name__)
app.secret_key = "demo-secret-not-for-production"

CYBERWATCH_URL = os.environ.get("CYBERWATCH_URL", "http://localhost:8000")
COMPANY_NAME = os.environ.get("COMPANY_NAME", "AcmeCorp")

# Valid credentials (demo only)
VALID_USERS = {
    "admin":   "password123",
    "ceo":     "Acme@2024",
    "hr.manager": "HRportal#9",
}

# Track failed attempts per IP (in-memory for demo)
failed_attempts = defaultdict(int)
failed_lock = threading.Lock()

# Track all login events for the demo log
login_events = []
events_lock = threading.Lock()


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")


def send_cyberwatch_alert(rule_id, rule_level, description, mitre_id, mitre_tactic,
                           mitre_technique, src_ip, user, raw_log, source="wazuh"):
    """Send a normalized alert to CyberWatch backend."""
    alert = {
        "alert_id": f"demo-{str(uuid.uuid4())}",
        "source": source,
        "timestamp": now_iso(),
        "agent": {
            "id": "010",
            "name": "acmecorp-webportal",
            "ip": "10.0.0.100",
        },
        "rule": {
            "id": rule_id,
            "level": rule_level,
            "description": description,
            "mitre": {
                "id": [mitre_id] if mitre_id else [],
                "tactic": [mitre_tactic] if mitre_tactic else [],
                "technique": [mitre_technique] if mitre_technique else [],
            },
        },
        "data": {
            "src_ip": src_ip,
            "dst_port": 5001,
            "user": user,
        },
        "raw_log": raw_log,
    }
    if REQUESTS_OK:
        try:
            req_lib.post(f"{CYBERWATCH_URL}/api/v1/alerts/ingest", json=alert, timeout=3)
        except Exception:
            pass  # Non-blocking — demo continues even if backend unreachable


def log_event(event_type, ip, username, success, message):
    with events_lock:
        login_events.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": event_type,
            "ip": ip,
            "user": username,
            "success": success,
            "message": message,
        })
        # Keep last 100 events
        if len(login_events) > 100:
            login_events.pop(0)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    attacker_ip = get_client_ip()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with failed_lock:
            attempts = failed_attempts[attacker_ip]

        if VALID_USERS.get(username) == password:
            # SUCCESS
            session["user"] = username
            session["ip"] = attacker_ip

            after_brute = failed_attempts[attacker_ip] >= 3
            
            # Send Wazuh alert — suspicious if login success after many failures
            if after_brute:
                send_cyberwatch_alert(
                    rule_id="5501",
                    rule_level=12,
                    description=f"Successful login after {failed_attempts[attacker_ip]} failed attempts — possible brute-force success: {username}",
                    mitre_id="T1078",
                    mitre_tactic="Initial Access",
                    mitre_technique="Valid Accounts",
                    src_ip=attacker_ip,
                    user=username,
                    raw_log=f"[{now_iso()}] SUSPICIOUS LOGIN: {username} authenticated from {attacker_ip} after {failed_attempts[attacker_ip]} failures"
                )
                log_event("BREACH", attacker_ip, username, True,
                          f"⚠️ Brute-force SUCCESS after {failed_attempts[attacker_ip]} attempts!")
            else:
                log_event("LOGIN", attacker_ip, username, True, "Normal login")

            with failed_lock:
                failed_attempts[attacker_ip] = 0
            return redirect(url_for("dashboard"))
        else:
            # FAILED LOGIN
            with failed_lock:
                failed_attempts[attacker_ip] += 1
                count = failed_attempts[attacker_ip]

            raw_log = f"[{now_iso()}] FAILED LOGIN: user='{username}' from={attacker_ip} attempt={count}"
            log_event("FAIL", attacker_ip, username, False, f"Failed attempt #{count}")

            # Always send failed login alert
            send_cyberwatch_alert(
                rule_id="5503",
                rule_level=10 if count < 5 else 13,
                description=f"Failed web login attempt #{count} for user '{username}' — {'BRUTE FORCE DETECTED' if count >= 5 else 'authentication failure'}",
                mitre_id="T1110",
                mitre_tactic="Credential Access",
                mitre_technique="Brute Force",
                src_ip=attacker_ip,
                user=username,
                raw_log=raw_log,
            )

            # At 5+ failures: also send high-severity burst alert
            if count == 5:
                send_cyberwatch_alert(
                    rule_id="5712",
                    rule_level=14,
                    description=f"Brute-force threshold exceeded: {count} failed logins from {attacker_ip} — AUTOMATED ATTACK LIKELY",
                    mitre_id="T1110.001",
                    mitre_tactic="Credential Access",
                    mitre_technique="Password Guessing",
                    src_ip=attacker_ip,
                    user=username,
                    raw_log=f"[{now_iso()}] ALERT: Brute-force threshold exceeded from {attacker_ip}",
                    source="suricata",
                )

            error = "Invalid username or password. Please try again."

            if count >= 10:
                error = "Account temporarily locked due to too many failed attempts."

    return render_template("login.html", error=error, company=COMPANY_NAME)


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"], company=COMPANY_NAME)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/status")
def status():
    """Internal endpoint to show current attack state (for demo)."""
    with failed_lock:
        attempts_data = dict(failed_attempts)
    with events_lock:
        recent = list(reversed(login_events[-20:]))
    return jsonify({
        "failed_attempts_by_ip": attempts_data,
        "recent_events": recent,
        "cyberwatch_url": CYBERWATCH_URL,
    })


@app.route("/reset")
def reset():
    """Reset all counters (for demo re-runs)."""
    with failed_lock:
        failed_attempts.clear()
    with events_lock:
        login_events.clear()
    return jsonify({"status": "reset", "message": "All counters cleared for fresh demo"})


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════╗
║        {COMPANY_NAME} Employee Portal — DEMO TARGET       ║
║                                                      ║
║  Running on: http://localhost:5001                   ║
║  CyberWatch: {CYBERWATCH_URL}         ║
║                                                      ║
║  Credentials (intentionally weak for demo):          ║
║    admin    / password123                            ║
║    ceo      / Acme@2024                              ║
║    hr.manager / HRportal#9                           ║
╚══════════════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=5001, debug=False)
