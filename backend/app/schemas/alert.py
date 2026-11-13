from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class MitreInfo(BaseModel):
    id: List[str] = []
    tactic: List[str] = []
    technique: List[str] = []

class AgentInfo(BaseModel):
    id: str = "000"
    name: str
    ip: str

class RuleInfo(BaseModel):
    id: str
    level: int
    description: str
    mitre: MitreInfo = Field(default_factory=MitreInfo)

class AlertData(BaseModel):
    src_ip: Optional[str] = None
    dst_port: Optional[int] = None
    user: Optional[str] = None

class AlertIngest(BaseModel):
    alert_id: str
    source: str = "wazuh"
    timestamp: datetime
    agent: AgentInfo
    rule: RuleInfo
    data: AlertData = Field(default_factory=AlertData)
    raw_log: Optional[str] = None

class AlertResponse(BaseModel):
    alert_id: str
    source: str
    timestamp: datetime
    agent_name: str
    rule_id: str
    rule_level: int
    rule_description: str
    incident_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
