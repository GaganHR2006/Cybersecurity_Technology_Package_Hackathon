import { useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import type { IncidentSummary } from '../../types';
import { SeverityBadge } from '../common/SeverityBadge';
import { StatusBadge } from '../common/StatusBadge';
import { RiskScoreRing } from '../common/RiskScoreRing';
import { ChevronRight, AlertTriangle } from 'lucide-react';

interface Props { incidents: IncidentSummary[]; isLoading: boolean; }

export function IncidentTable({ incidents, isLoading }: Props) {
  const nav = useNavigate();
  if (isLoading) return <div className="flex items-center justify-center h-48 text-gray-500 text-sm">Loading incidents...</div>;
  if (!incidents.length) return (
    <div className="flex flex-col items-center justify-center h-48 text-gray-500 gap-2">
      <AlertTriangle className="w-6 h-6" /><p className="text-sm">No incidents found</p>
    </div>
  );
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b border-gray-800 text-xs uppercase tracking-wider">
            <th className="pb-3 pl-4 pr-2">Risk</th>
            <th className="pb-3 pr-4">Incident</th>
            <th className="pb-3 pr-4">Severity</th>
            <th className="pb-3 pr-4">Status</th>
            <th className="pb-3 pr-4">Target</th>
            <th className="pb-3 pr-4">Alerts</th>
            <th className="pb-3 pr-4">First Seen</th>
            <th className="pb-3 pr-4"></th>
          </tr>
        </thead>
        <tbody>
          {incidents.map(inc => (
            <tr key={inc.incident_id} onClick={() => nav(`/incidents/${inc.incident_id}`)}
              className="border-b border-gray-800/50 hover:bg-gray-800/30 cursor-pointer transition-colors group">
              <td className="py-3 pl-4 pr-2"><RiskScoreRing score={inc.risk_score} size={48} /></td>
              <td className="py-3 pr-4 max-w-xs">
                <div className="font-medium text-gray-100 truncate">{inc.title}</div>
                <div className="text-gray-600 text-xs font-mono mt-0.5">{inc.incident_id}</div>
              </td>
              <td className="py-3 pr-4"><SeverityBadge severity={inc.severity} /></td>
              <td className="py-3 pr-4"><StatusBadge status={inc.status} /></td>
              <td className="py-3 pr-4 text-cyan-400 font-mono text-xs">{inc.primary_entity_id ?? '—'}</td>
              <td className="py-3 pr-4 text-gray-400">{inc.alert_count}</td>
              <td className="py-3 pr-4 text-gray-500 text-xs">
                {inc.first_seen ? formatDistanceToNow(new Date(inc.first_seen), { addSuffix: true }) : '—'}
              </td>
              <td className="py-3 pr-4">
                <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-cyan-400 transition-colors" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
