import { useQuery } from '@tanstack/react-query';
import { metricsApi } from '../services/api';
import { Activity } from 'lucide-react';

export function MetricsPage() {
  const { data: m, isLoading } = useQuery({ queryKey: ['metrics'], queryFn: metricsApi.get, refetchInterval: 10000 });
  if (isLoading) return <div className="pt-20 text-center text-gray-500 text-sm">Loading metrics...</div>;

  const cards = [
    { label: 'Total Alerts Ingested', value: m?.total_alerts_ingested ?? 0, color: 'text-cyan-400' },
    { label: 'Total Incidents', value: m?.total_incidents_created ?? 0, color: 'text-blue-400' },
    { label: 'Open Incidents', value: m?.open_incidents ?? 0, color: 'text-orange-400' },
    { label: 'Critical', value: m?.critical_incidents ?? 0, color: 'text-red-400' },
    { label: 'High', value: m?.high_incidents ?? 0, color: 'text-orange-300' },
    { label: 'Medium', value: m?.medium_incidents ?? 0, color: 'text-yellow-400' },
    { label: 'Low', value: m?.low_incidents ?? 0, color: 'text-green-400' },
    { label: 'False Positives', value: m?.false_positive_count ?? 0, color: 'text-gray-400' },
    { label: 'False Positive Rate', value: `${(m?.false_positive_rate ?? 0).toFixed(1)}%`, color: 'text-purple-400' },
    { label: 'Avg Alerts / Incident', value: (m?.avg_alerts_per_incident ?? 0).toFixed(1), color: 'text-teal-400' },
    { label: 'Response Actions', value: m?.total_response_actions ?? 0, color: 'text-blue-300' },
    { label: 'Pending Approvals', value: m?.pending_approvals ?? 0, color: 'text-yellow-500' },
  ];

  return (
    <div className="pt-14 min-h-screen">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-center gap-2 mb-6">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h1 className="text-2xl font-bold text-white">Platform Metrics</h1>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {cards.map(c => (
            <div key={c.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="text-xs text-gray-500 mb-2 uppercase tracking-wide">{c.label}</div>
              <div className={`text-3xl font-bold ${c.color}`}>{c.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
