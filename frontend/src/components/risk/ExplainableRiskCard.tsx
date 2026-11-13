import type { RiskFactor } from '../../types';
import { RiskScoreRing } from '../common/RiskScoreRing';
import { Info } from 'lucide-react';

interface Props { score: number; confidence: number; severity: string; factors: RiskFactor[]; }

export function ExplainableRiskCard({ score, confidence, severity, factors }: Props) {
  const maxW = Math.max(...factors.map(f => f.weight), 1);
  const sevColor = severity === 'CRITICAL' ? 'text-red-400' : severity === 'HIGH' ? 'text-orange-400'
    : severity === 'MEDIUM' ? 'text-yellow-400' : 'text-green-400';
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
        <Info className="w-3.5 h-3.5 text-cyan-400" />Risk Score Breakdown
      </h3>
      <div className="flex items-center gap-5 mb-5">
        <RiskScoreRing score={Math.round(score)} size={76} />
        <div>
          <div className="text-2xl font-bold text-white">{score.toFixed(1)}<span className="text-gray-500 text-sm font-normal">/100</span></div>
          <div className="text-xs text-gray-400 mt-0.5">Confidence: {(confidence * 100).toFixed(0)}%</div>
          <div className={`text-xs font-bold mt-1 uppercase tracking-wide ${sevColor}`}>{severity}</div>
        </div>
      </div>
      <div className="space-y-3">
        {factors.map((f, i) => (
          <div key={i}>
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs font-medium text-gray-300">{f.factor}</span>
              <span className="text-xs font-mono text-cyan-400">+{f.weight.toFixed(1)}</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-1.5">
              <div className="h-1.5 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all"
                style={{ width: `${(f.weight / maxW) * 100}%` }} />
            </div>
            <p className="text-xs text-gray-500 mt-1">{f.detail}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
