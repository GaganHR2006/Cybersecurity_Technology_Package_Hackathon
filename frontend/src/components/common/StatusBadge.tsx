import type { IncidentStatus } from '../../types';

const cfg: Record<IncidentStatus, string> = {
  OPEN:          'bg-blue-900/50 text-blue-300 border border-blue-700/50',
  UNDER_REVIEW:  'bg-purple-900/50 text-purple-300 border border-purple-700/50',
  CONTAINED:     'bg-teal-900/50 text-teal-300 border border-teal-700/50',
  RESOLVED:      'bg-green-900/50 text-green-300 border border-green-700/50',
  FALSE_POSITIVE:'bg-gray-800 text-gray-400 border border-gray-700',
};

export function StatusBadge({ status }: { status: IncidentStatus }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs ${cfg[status] ?? cfg.OPEN}`}>
      {status.replace('_', ' ')}
    </span>
  );
}
