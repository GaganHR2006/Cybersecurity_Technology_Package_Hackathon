import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { incidentsApi, metricsApi } from '../services/api';
import { IncidentTable } from '../components/incidents/IncidentTable';
import { Shield, AlertTriangle, TrendingUp, CheckCircle } from 'lucide-react';

export function Dashboard() {
  const [statusF, setStatusF] = useState('');
  const [sevF, setSevF] = useState('');

  const { data: incidents = [], isLoading } = useQuery({
    queryKey: ['incidents', statusF, sevF],
    queryFn: () => incidentsApi.list({ status: statusF || undefined, severity: sevF || undefined }),
    refetchInterval: 10000,
  });

  const { data: m } = useQuery({ queryKey: ['metrics'], queryFn: metricsApi.get, refetchInterval: 10000 });

  const stats = [
    { label: 'Total Alerts', value: m?.total_alerts_ingested ?? '—', icon: Shield, color: 'text-cyan-400' },
    { label: 'Open Incidents', value: m?.open_incidents ?? '—', icon: AlertTriangle, color: 'text-orange-400' },
    { label: 'Critical', value: m?.critical_incidents ?? '—', icon: TrendingUp, color: 'text-red-400' },
    { label: 'False Positive Rate', value: m ? `${m.false_positive_rate.toFixed(1)}%` : '—', icon: CheckCircle, color: 'text-green-400' },
  ];

  return (
    <div className="pt-14 min-h-screen">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">Incident Triage Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Real-time correlated security incidents — prioritized by risk score</p>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {stats.map(s => (
            <div key={s.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-500 uppercase tracking-wide">{s.label}</span>
                <s.icon className={`w-4 h-4 ${s.color}`} />
              </div>
              <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
            </div>
          ))}
        </div>
        <div className="flex gap-3 mb-4 flex-wrap items-center">
          <select value={statusF} onChange={e => setStatusF(e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 focus:border-cyan-500 focus:outline-none">
            <option value="">All Statuses</option>
            {['OPEN','UNDER_REVIEW','CONTAINED','RESOLVED','FALSE_POSITIVE'].map(s => (
              <option key={s} value={s}>{s.replace('_',' ')}</option>
            ))}
          </select>
          <select value={sevF} onChange={e => setSevF(e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 focus:border-cyan-500 focus:outline-none">
            <option value="">All Severities</option>
            {['CRITICAL','HIGH','MEDIUM','LOW'].map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <span className="text-xs text-gray-500 ml-auto">{incidents.length} incident(s) · auto-refreshes every 10s</span>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <IncidentTable incidents={incidents} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
