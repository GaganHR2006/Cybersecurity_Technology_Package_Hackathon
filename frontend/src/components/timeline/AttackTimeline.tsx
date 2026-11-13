import { format } from 'date-fns';
import type { TimelineStep } from '../../types';
import { Shield, Zap, Database, Upload, AlertOctagon, type LucideIcon } from 'lucide-react';

const tacticStyle: Record<string, { icon: LucideIcon; cls: string }> = {
  'Credential Access': { icon: Shield,       cls: 'text-yellow-400 bg-yellow-900/40 border-yellow-700/50' },
  'Initial Access':    { icon: Zap,          cls: 'text-orange-400 bg-orange-900/40 border-orange-700/50' },
  'Collection':        { icon: Database,     cls: 'text-blue-400 bg-blue-900/40 border-blue-700/50' },
  'Exfiltration':      { icon: Upload,       cls: 'text-red-400 bg-red-900/40 border-red-700/50' },
  'Impact':            { icon: AlertOctagon, cls: 'text-red-500 bg-red-900/60 border-red-600/70' },
  'Execution':         { icon: Zap,          cls: 'text-purple-400 bg-purple-900/40 border-purple-700/50' },
};

function getStyle(stage: string) {
  for (const [tactic, style] of Object.entries(tacticStyle)) {
    if (stage.includes(tactic)) return style;
  }
  return { icon: AlertOctagon, cls: 'text-gray-400 bg-gray-800 border-gray-700' };
}

export function AttackTimeline({ steps }: { steps: TimelineStep[] }) {
  return (
    <div className="space-y-0">
      {steps.map((step, i) => {
        const { icon: Icon, cls } = getStyle(step.stage);
        return (
          <div key={step.step} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className={`w-9 h-9 rounded-full border flex items-center justify-center flex-shrink-0 ${cls}`}>
                <Icon className="w-4 h-4" />
              </div>
              {i < steps.length - 1 && <div className="w-px flex-1 bg-gray-800 my-1" />}
            </div>
            <div className="pb-5 flex-1">
              <div className="flex items-center gap-2 mb-0.5">
                <span className={`text-xs font-semibold uppercase tracking-wide ${cls.split(' ')[0]}`}>
                  Step {step.step}: {step.stage.split(' / ')[0]}
                </span>
                <span className="text-xs text-gray-600 font-mono">
                  {format(new Date(step.timestamp), 'HH:mm:ss')}
                </span>
              </div>
              <p className="text-sm text-gray-200">{step.summary}</p>
              <p className="text-xs text-gray-600 mt-0.5 font-mono">{step.alert_id}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
