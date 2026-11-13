# CyberWatch Demo — Brute Force Attacker

This script simulates a real-world brute-force / credential stuffing attack
against the AcmeCorp demo login page to demonstrate CyberWatch detection.

## Setup

```bash
pip install requests
```

## Usage

```bash
# Default: attack the 'admin' account
python brute_force.py

# Attack a different account
python brute_force.py --user ceo

# Slower (more realistic), different target
python brute_force.py --user admin --delay 1.0 --target http://localhost:5001
```

## What to watch

1. Open **http://localhost:5173** (CyberWatch dashboard) before running
2. Run this script
3. After ~5 attempts: a **HIGH** incident appears in CyberWatch
4. After password found: incident escalates to **CRITICAL**
5. CyberWatch recommends "Revoke User Session" — analyst can approve it
