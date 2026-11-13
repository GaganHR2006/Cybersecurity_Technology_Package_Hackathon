# Open-Source Intelligent Cybersecurity Monitoring & Incident Response Platform

A Wazuh-based security platform featuring an intelligent event-correlation layer, explainable contextual risk prioritization, human-in-the-loop analyst-approved response workflows, and upstream Wazuh contributions.

## Documentation & Architecture Plan

- **Full Implementation Plan**: [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md)
- **Architecture**: Monorepo layout combining FastAPI backend, React+TypeScript analyst dashboard, telemetry simulation lab, and upstream Wazuh decoder contributions.

## Four-Agent Division of Labor

| Agent | Domain | Key Responsibilities | Primary Directories |
|---|---|---|---|
| **Agent 1** | **Network Security & Lab** | TCP/IP, Suricata logs, attack simulation scripts (brute force, exfil), Docker lab orchestration | `lab_simulation/`, `docker-compose.yml` |
| **Agent 2** | **Detection & Threat Intel** | MITRE ATT&CK mapping, Wazuh decoders/rules, upstream fix for issue #41226 (pfSense) | `upstream_contributions/`, `backend/app/services/threat_intel.py` |
| **Agent 3** | **Backend & Correlation Engine** | FastAPI app, sliding-window correlation algorithm, explainable risk scoring, response workflow & audit store | `backend/` |
| **Agent 4** | **SOC Analyst Frontend & QA** | React + TypeScript + Tailwind UI, attack timeline, risk factor breakdown, response modal, metric validation | `frontend/` |
