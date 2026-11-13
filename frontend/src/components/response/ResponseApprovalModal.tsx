import { useState } from 'react';
import { X, ShieldCheck, ShieldOff, AlertTriangle } from 'lucide-react';
import type { RecommendedAction } from '../../types';

interface Props {
  action: RecommendedAction;
  onApprove: (analyst: string, notes: string) => Promise<void>;
  onReject: (analyst: string, reason: string) => Promise<void>;
  onClose: () => void;
}

export function ResponseApprovalModal({ action, onApprove, onReject, onClose }: Props) {
  const [mode, setMode] = useState<'choose' | 'approve' | 'reject'>('choose');
  const [analyst, setAnalyst] = useState('');
  const [notes, setNotes] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (fn: () => Promise<void>) => {
    if (!analyst.trim()) { setError('Analyst name is required'); return; }
    if (mode === 'reject' && !reason.trim()) { setError('Rejection reason is mandatory'); return; }
    setLoading(true); setError('');
    try { await fn(); onClose(); }
    catch (e: any) { setError(e?.response?.data?.detail ?? 'Request failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl w-full max-w-lg">
        <div className="flex items-center justify-between p-5 border-b border-gray-800">
          <div className="flex items-center gap-2 text-yellow-400 font-semibold text-sm">
            <AlertTriangle className="w-4 h-4" />Response Action Review
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-200"><X className="w-5 h-5" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm font-semibold text-white mb-1">{action.name}</div>
            <div className="text-sm text-gray-300 mb-2">{action.description}</div>
            <div className="text-xs text-gray-500">Target: <span className="text-cyan-400 font-mono">{action.target}</span></div>
          </div>
          {error && <div className="text-red-400 text-xs bg-red-900/30 border border-red-800 rounded p-2">{error}</div>}
          {mode === 'choose' && (
            <div className="flex gap-3">
              <button onClick={() => setMode('approve')}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-green-800/40 hover:bg-green-700/50 text-green-300 border border-green-700/50 rounded-lg text-sm font-medium transition-colors">
                <ShieldCheck className="w-4 h-4" />Approve
              </button>
              <button onClick={() => setMode('reject')}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-red-800/40 hover:bg-red-700/50 text-red-300 border border-red-700/50 rounded-lg text-sm font-medium transition-colors">
                <ShieldOff className="w-4 h-4" />Reject
              </button>
            </div>
          )}
          {mode !== 'choose' && (
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-400 block mb-1">Analyst ID *</label>
                <input value={analyst} onChange={e => setAnalyst(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
                  placeholder="e.g. john.doe" />
              </div>
              {mode === 'approve' ? (
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Notes (optional)</label>
                  <textarea value={notes} onChange={e => setNotes(e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none h-16 resize-none" />
                </div>
              ) : (
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Rejection Reason * (required for audit)</label>
                  <textarea value={reason} onChange={e => setReason(e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-red-500 focus:outline-none h-16 resize-none"
                    placeholder="Explain why this action is being rejected..." />
                </div>
              )}
              <div className="flex gap-2">
                <button onClick={() => { setMode('choose'); setError(''); }}
                  className="flex-1 py-2 text-sm text-gray-400 hover:text-gray-200 border border-gray-700 rounded-lg">Back</button>
                {mode === 'approve' ? (
                  <button onClick={() => submit(() => onApprove(analyst, notes))} disabled={loading}
                    className="flex-1 py-2 text-sm font-medium text-white bg-green-700 hover:bg-green-600 rounded-lg disabled:opacity-50">
                    {loading ? 'Approving...' : 'Confirm Approve'}
                  </button>
                ) : (
                  <button onClick={() => submit(() => onReject(analyst, reason))} disabled={loading}
                    className="flex-1 py-2 text-sm font-medium text-white bg-red-700 hover:bg-red-600 rounded-lg disabled:opacity-50">
                    {loading ? 'Rejecting...' : 'Confirm Reject'}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
