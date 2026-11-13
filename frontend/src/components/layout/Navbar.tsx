import { Shield, Activity } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/audit', label: 'Audit Log' },
  { to: '/metrics', label: 'Metrics' },
];

export function Navbar() {
  const { pathname } = useLocation();
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-14 bg-gray-900/95 border-b border-gray-800 backdrop-blur flex items-center px-6 gap-6">
      <div className="flex items-center gap-2 text-cyan-400 font-bold text-lg mr-4">
        <Shield className="w-5 h-5" />
        <span>CyberWatch</span>
      </div>
      {links.map(l => (
        <Link key={l.to} to={l.to}
          className={`text-sm font-medium transition-colors ${pathname === l.to ? 'text-cyan-400' : 'text-gray-400 hover:text-gray-200'}`}>
          {l.label}
        </Link>
      ))}
      <div className="ml-auto flex items-center gap-2 text-xs">
        <Activity className="w-4 h-4 text-green-400" />
        <span className="text-green-400">System Online</span>
      </div>
    </nav>
  );
}
