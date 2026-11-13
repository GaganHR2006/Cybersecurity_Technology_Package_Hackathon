from pydantic import BaseModel

class MetricsResponse(BaseModel):
    total_alerts_ingested: int
    total_incidents_created: int
    open_incidents: int
    critical_incidents: int
    high_incidents: int
    medium_incidents: int
    low_incidents: int
    false_positive_count: int
    false_positive_rate: float
    avg_alerts_per_incident: float
    total_response_actions: int
    pending_approvals: int
