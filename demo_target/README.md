# AcmeCorp Demo Target — Fake Company Login Portal

A realistic mock corporate login page used to demonstrate CyberWatch detection.

## Run

```bash
pip install flask requests
python app.py
```

Open: http://localhost:5001

## Credentials

| Username | Password | Role |
|---|---|---|
| admin | password123 | Administrator |
| ceo | Acme@2024 | CEO |
| hr.manager | HRportal#9 | HR Manager |

## Endpoints

| URL | Purpose |
|---|---|
| `http://localhost:5001/login` | Login page |
| `http://localhost:5001/status` | Attack status JSON |
| `http://localhost:5001/reset` | Reset counters for re-demo |
