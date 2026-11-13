import type { Severity } from '../../types';

const cfg: Record<Severity, { cls: string }> = {
  CRITICAL: { cls: 'bg-red-900/50 text-red-400 border border-red-700/50 font-bold' },
  HIGH:     { cls: 'bg-orange-900/50 text-orange-400 border border-orange-700/50 font-bold' },
  MEDIUM:   { cls: 'bg-yellow-900/50 text-yellow-400 border border-yellow-700/50' },
  LOW:      { cls: 'bg-green-900/50 text-green-400 border border-green-700/50' },
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  const c = cfg[severity] ?? cfg.LOW;
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs uppercase tracking-wide ${c.cls}`}>
      {severity}
    </span>
  );
}
