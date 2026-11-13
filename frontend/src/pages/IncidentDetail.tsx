import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { incidentsApi, responsesApi } from '../services/api';
import { AttackTimeline } from '../components/timeline/AttackTimeline';
import { ExplainableRiskCard } from '../components/risk/ExplainableRiskCard';
import { ResponseApprovalModal } from '../components/response/ResponseApprovalModal';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { StatusBadge } from '../components/common/StatusBadge';
import { ArrowLeft, Clock, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { format } from 'date-fns';
import type { RecommendedAction, ResponseAction } from '../types';

export function IncidentDetail() {
  const { id } = useParams<{ id: string }>();
  const nav = useNavigate();
  const qc = useQueryClient();
  const [selectedAction, setSelectedAction] = useState<RecommendedAction | null>(null);

  const { data: incident, isLoading } = useQuery({
    queryKey: ['incident', id],
    queryFn: () => incidentsApi.get(id!),
    enabled: !!id,
  });

  const { data: actions = [] } = useQuery({
    queryKey: ['actions', id],
    queryFn: () => responsesApi.getForIncident(id!),
    enabled: !!id,
    refetchInterval: 5000,
  });

  const approveMut = useMutation({
    mutationFn: ({ actionId, analyst, notes }: { actionId: string; analyst: string; notes: string }) =>
      responsesApi.approve(actionId, analyst, notes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['actions', id] }),
  });

  const rejectMut = useMutation({
    mutationFn: ({ actionId, analyst, reason }: { actionId: string; analyst: string; reason: string }) =>
      responsesApi.reject(actionId, analyst, reason),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['actions', id] }),
  });

  const updateStatus = async (status: string) => {
    if (!id) return;
    await incidentsApi.updateStatus(id, status, 'analyst');
    qc.invalidateQueries({ queryKey: ['incident', id] });
    qc.invalidateQueries({ queryKey: ['incidents'] });
  };

  if (isLoading) return <div className="pt-20 text-center text-gray-500 text-sm">Loading...</div>;
  if (!incident) return <div className="pt-20 text-center text-gray-500 text-sm">Incident not found</div>;

  const pending = actions.filter((a: ResponseAction) => a.status === 'PENDING_APPROVAL');
  const done = actions.filter((a: ResponseAction) => a.status !== 'PENDING_APPROVAL');

  return (
    <div className="pt-14 min-h-screen">
      <div className="max-w-7xl mx-auto px-6 py-6">
        <button onClick={() => nav('/')} className="flex items-center gap-2 text-gray-400 hover:text-gray-200 text-sm mb-4 transition-colors">
          <ArrowLeft className="w-4 h-4" />Back to Dashboard
        </button>
        <div className="flex items-start justify-between mb-5 gap-4 flex-wrap">
          <div>
            <h1 className="text-xl font-bold text-white mb-2">{incident.title}</h1>
            <div className="flex items-center gap-3 flex-wrap">
              <SeverityBadge severity={incident.severity} />
              <StatusBadge status={incident.status} />
              <span className="text-xs font-mono text-gray-600">{incident.incident_id}</span>
              {incident.first_seen && (
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <Clock className="w-3 h-3" />{format(new Date(incident.first_seen), 'MMM d, HH:mm:ss')}
                </span>
              )}
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            {incident.status === 'OPEN' && (
              <button onClick={() => updateStatus('UNDER_REVIEW')}
                className="text-xs px-3 py-1.5 bg-purple-800/40 hover:bg-purple-700/50 text-purple-300 border border-purple-700/50 rounded-lg transition-colors">
                Mark Under Review
              </button>
            )}
            {!['RESOLVED','FALSE_POSITIVE'].includes(incident.status) && (
              <>
                <button onClick={() => updateStatus('FALSE_POSITIVE')}
                  className="text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-400 border border-gray-700 rounded-lg transition-colors">
                  False Positive
                </button>
                <button onClick={() => updateStatus('RESOLVED')}
                  className="text-xs px-3 py-1.5 bg-green-800/40 hover:bg-green-700/50 text-green-300 border border-green-700/50 rounded-lg transition-colors">
                  Resolve
                </button>
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {[
            { label: 'Target', value: incident.primary_entity_id ?? '—' },
            { label: 'Entity IP', value: incident.primary_entity_ip ?? '—' },
            { label: 'Alerts', value: String(incident.alert_ids.length) },
            { label: 'Tactics', value: incident.tactics_observed.length > 0 ? incident.tactics_observed.join(', ') : '—' },
          ].map(m => (
            <div key={m.label} className="bg-gray-900 border border-gray-800 rounded-xl p-3">
              <div className="text-xs text-gray-500 mb-1">{m.label}</div>
              <div className="text-sm text-white font-medium truncate" title={m.value}>{m.value}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-5">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Attack Timeline</h3>
              {incident.attack_timeline.length > 0
                ? <AttackTimeline steps={incident.attack_timeline} />
                : <p className="text-gray-500 text-sm">No timeline data.</p>}
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Response Actions</h3>
              {pending.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs text-yellow-400 mb-3 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />{pending.length} action(s) awaiting approval
                  </p>
                  {pending.map((a: ResponseAction) => {
                    const rec = incident.recommended_actions.find(r => r.action_id === a.action_id);
                    return (
                      <div key={a.action_id} className="border border-yellow-700/30 bg-yellow-900/10 rounded-lg p-3 mb-2">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="text-sm font-medium text-yellow-200">{a.name}</div>
                            <div className="text-xs text-gray-400 mt-0.5">{a.description}</div>
                            <div className="text-xs text-gray-500 mt-1">Target: <span className="text-cyan-400 font-mono">{a.target}</span></div>
                          </div>
                          <button onClick={() => rec && setSelectedAction(rec)}
                            className="flex-shrink-0 text-xs px-3 py-1.5 bg-yellow-700/40 hover:bg-yellow-600/50 text-yellow-300 border border-yellow-600/50 rounded-lg transition-colors">
                            Review
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
              {done.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs text-gray-500 mb-2">Completed Actions</p>
                  {done.map((a: ResponseAction) => (
                    <div key={a.action_id} className={`rounded-lg p-3 border flex items-start gap-3 ${
                      a.status === 'EXECUTED' ? 'border-green-800/40 bg-green-900/10' : 'border-red-800/40 bg-red-900/10'}`}>
                      {a.status === 'EXECUTED'
                        ? <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                        : <XCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />}
                      <div>
                        <div className={`text-sm font-medium ${a.status === 'EXECUTED' ? 'text-green-200' : 'text-red-200'}`}>{a.name}</div>
                        <div className="text-xs text-gray-400 mt-0.5">
                          {a.status === 'REJECTED' ? `Rejected: ${a.rejection_reason}` : `Executed by ${a.approved_by}`}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {pending.length === 0 && done.length === 0 && (
                <p className="text-gray-500 text-sm">No response actions available.</p>
              )}
            </div>
          </div>
          <div>
            <ExplainableRiskCard score={incident.risk_score} confidence={incident.confidence}
              severity={incident.severity} factors={incident.risk_factors} />
          </div>
        </div>
      </div>

      {selectedAction && (
        <ResponseApprovalModal
          action={selectedAction}
          onApprove={async (analyst, notes) => { await approveMut.mutateAsync({ actionId: selectedAction.action_id, analyst, notes }); }}
          onReject={async (analyst, reason) => { await rejectMut.mutateAsync({ actionId: selectedAction.action_id, analyst, reason }); }}
          onClose={() => setSelectedAction(null)}
        />
      )}
    </div>
  );
}
