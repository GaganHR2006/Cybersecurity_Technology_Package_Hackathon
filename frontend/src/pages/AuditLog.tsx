import { useQuery } from '@tanstack/react-query';
import { metricsApi } from '../services/api';
import { format } from 'date-fns';
import { Shield } from 'lucide-react';
import type { AuditEntry } from '../types';

const eventColor: Record<string, string> = {
  ALERT_INGESTED: 'text-blue-400',
  INCIDENT_CREATED: 'text-orange-400',
  ACTION_APPROVED_AND_EXECUTED: 'text-green-400',
  ACTION_REJECTED: 'text-red-400',
  INCIDENT_STATUS_CHANGED: 'text-purple-400',
};

export function AuditLog() {
  const { data: logs = [], isLoading } = useQuery({
    queryKey: ['audit-log'],
    queryFn: metricsApi.getAuditLog,
    refetchInterval: 10000,
  });
  return (
    <div className="pt-14 min-h-screen">
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="flex items-center gap-2 mb-2">
          <Shield className="w-5 h-5 text-cyan-400" />
          <h1 className="text-2xl font-bold text-white">SOC Audit Trail</h1>
        </div>
        <p className="text-gray-400 text-sm mb-6">Immutable record of all system events and analyst actions.</p>
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center h-48 text-gray-500 text-sm">Loading...</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-800 text-xs uppercase tracking-wider">
                  <th className="pb-3 p-4">Time</th>
                  <th className="pb-3 pr-4">Event</th>
                  <th className="pb-3 pr-4">Reference</th>
                  <th className="pb-3 pr-4">Analyst</th>
                  <th className="pb-3 pr-4">Detail</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((l: AuditEntry) => (
                  <tr key={l.id} className="border-b border-gray-800/50 hover:bg-gray-800/20">
                    <td className="py-2.5 pl-4 pr-4 text-xs text-gray-500 whitespace-nowrap font-mono">
                      {format(new Date(l.created_at), 'MMM d HH:mm:ss')}
                    </td>
                    <td className="py-2.5 pr-4">
                      <span className={`text-xs font-semibold ${eventColor[l.event_type] ?? 'text-gray-400'}`}>
                        {l.event_type.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="py-2.5 pr-4 text-xs font-mono text-gray-500 max-w-[8rem] truncate">
                      {l.incident_id ?? l.action_id ?? '—'}
                    </td>
                    <td className="py-2.5 pr-4 text-xs text-gray-300">{l.analyst ?? '—'}</td>
                    <td className="py-2.5 pr-4 text-xs text-gray-400 max-w-sm truncate">{l.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
