export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type IncidentStatus = 'OPEN' | 'UNDER_REVIEW' | 'CONTAINED' | 'RESOLVED' | 'FALSE_POSITIVE';
export type ActionStatus = 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXECUTED' | 'FAILED';

export interface RiskFactor {
  factor: string;
  weight: number;
  detail: string;
}

export interface TimelineStep {
  step: number;
  stage: string;
  timestamp: string;
  alert_id: string;
  summary: string;
}

export interface RecommendedAction {
  action_id: string;
  name: string;
  description: string;
  requires_approval: boolean;
  target: string;
  status: ActionStatus;
}

export interface Incident {
  incident_id: string;
  title: string;
  status: IncidentStatus;
  severity: Severity;
  risk_score: number;
  confidence: number;
  primary_entity_type: string | null;
  primary_entity_id: string | null;
  primary_entity_ip: string | null;
  risk_factors: RiskFactor[];
  attack_timeline: TimelineStep[];
  recommended_actions: RecommendedAction[];
  alert_ids: string[];
  tactics_observed: string[];
  first_seen: string | null;
  last_seen: string | null;
  created_at: string;
  analyst_notes: string | null;
}

export interface IncidentSummary {
  incident_id: string;
  title: string;
  status: IncidentStatus;
  severity: Severity;
  risk_score: number;
  primary_entity_id: string | null;
  alert_count: number;
  first_seen: string | null;
  last_seen: string | null;
  created_at: string;
}

export interface ResponseAction {
  action_id: string;
  incident_id: string;
  name: string;
  description: string;
  target: string;
  status: ActionStatus;
  approved_by: string | null;
  approved_at: string | null;
  rejection_reason: string | null;
  created_at: string;
}

export interface Metrics {
  total_alerts_ingested: number;
  total_incidents_created: number;
  open_incidents: number;
  critical_incidents: number;
  high_incidents: number;
  medium_incidents: number;
  low_incidents: number;
  false_positive_count: number;
  false_positive_rate: number;
  avg_alerts_per_incident: number;
  total_response_actions: number;
  pending_approvals: number;
}

export interface AuditEntry {
  id: number;
  event_type: string;
  incident_id: string | null;
  action_id: string | null;
  analyst: string | null;
  detail: string;
  created_at: string;
}
