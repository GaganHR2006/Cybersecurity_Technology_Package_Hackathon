import axios from 'axios';
import type { Incident, IncidentSummary, ResponseAction, Metrics, AuditEntry } from '../types';

const api = axios.create({ baseURL: '/api/v1' });

export const incidentsApi = {
  list: (params?: { status?: string; severity?: string }) =>
    api.get<IncidentSummary[]>('/incidents/', { params }).then(r => r.data),
  get: (id: string) =>
    api.get<Incident>(`/incidents/${id}`).then(r => r.data),
  updateStatus: (id: string, status: string, analyst: string, notes?: string) =>
    api.patch<Incident>(`/incidents/${id}/status`, { status, analyst, analyst_notes: notes }).then(r => r.data),
};

export const responsesApi = {
  getForIncident: (id: string) =>
    api.get<ResponseAction[]>(`/responses/incident/${id}`).then(r => r.data),
  approve: (actionId: string, analyst: string, notes?: string) =>
    api.post<ResponseAction>(`/responses/${actionId}/approve`, { analyst, notes }).then(r => r.data),
  reject: (actionId: string, analyst: string, reason: string) =>
    api.post<ResponseAction>(`/responses/${actionId}/reject`, { analyst, reason }).then(r => r.data),
};

export const metricsApi = {
  get: () => api.get<Metrics>('/metrics/').then(r => r.data),
  getAuditLog: () => api.get<AuditEntry[]>('/metrics/audit-log').then(r => r.data),
};
