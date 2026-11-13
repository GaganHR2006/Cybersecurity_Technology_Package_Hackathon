# CyberWatch Lab Simulation

This directory contains realistic attack scenario simulators and test fixtures for the CyberWatch Intelligence Platform.

## Threat Scenarios

### Scenario 1: Account Takeover & Data Exfiltration
Multi-stage attack on `prod-db-server`:
1. 15× SSH brute force attempts (MITRE T1110 - Credential Access)
2. Successful authentication from external IP (MITRE T1078 - Initial Access)
3. Sensitive database file read (MITRE T1005 - Collection)
4. 450MB outbound data transfer (MITRE T1048 - Exfiltration)

### Scenario 2: Ransomware Preparation
Attack chain on `win-workstation-01`:
1. Suspicious PowerShell download (MITRE T1059.001 - Execution)
2. 20× rapid file modifications (MITRE T1486 - Impact)
3. Shadow copy deletion (MITRE T1490 - Impact)

### Scenario 3: Benign Background Activity
Normal admin activity on `ops-server-01` (should produce low/no incidents):
- Routine SSH logins, package updates, backup jobs

## Usage

### Run the simulator

```bash
# Run scenario 1 (Account Takeover)
python generators/attack_simulator.py --scenario 1

# Run scenario 2 (Ransomware Prep)
python generators/attack_simulator.py --scenario 2

# Run all scenarios
python generators/attack_simulator.py --scenario all

# Custom backend URL and delay
python generators/attack_simulator.py --scenario all --backend-url http://my-backend:8000 --delay 1.0
```

### Use offline fixture files
The JSON scenario files can be used directly for backend unit testing:
```python
import json
with open("lab_simulation/test_fixtures/wazuh_alerts_sample.json") as f:
    alerts = json.load(f)
```

### Generate pfSense/Suricata samples
```bash
python generators/pfsense_suricata_feed.py
```
Outputs: `test_fixtures/pfsense_samples.log` and `test_fixtures/suricata_eve_samples.json`

## Docker Usage
The `docker-compose.yml` at the project root automatically runs scenario "all" after the backend starts:
```bash
docker-compose up
```
