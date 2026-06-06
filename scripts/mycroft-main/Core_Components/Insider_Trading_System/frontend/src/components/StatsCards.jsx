import React from 'react';
import { Activity, CheckCircle, AlertCircle, XCircle, TrendingUp } from 'lucide-react';

export default function StatsCards({ stats }) {
  return (
    <div className="grid grid-cols-5 gap-3 mb-6">
      <StatCard title="Total Trades" value={stats.total_trades} icon={<Activity className="w-5 h-5" />} color="blue" />
      <StatCard title="Analyzed" value={stats.analyzed_trades} icon={<CheckCircle className="w-5 h-5" />} color="green" />
      <StatCard title="Pending" value={stats.unanalyzed_trades} icon={<AlertCircle className="w-5 h-5" />} color="yellow" />
      <StatCard title="Failed" value={stats.failed_analyses} icon={<XCircle className="w-5 h-5" />} color="red" />
      <StatCard title="Success Rate" value={`${stats.success_rate}%`} icon={<TrendingUp className="w-5 h-5" />} color="purple" />
    </div>
  );
}

function StatCard({ title, value, icon, color }) {
  const colors = {
    blue: 'from-blue-600/20 to-blue-600/5 border-blue-600/30',
    green: 'from-green-600/20 to-green-600/5 border-green-600/30',
    yellow: 'from-yellow-600/20 to-yellow-600/5 border-yellow-600/30',
    red: 'from-red-600/20 to-red-600/5 border-red-600/30',
    purple: 'from-purple-600/20 to-purple-600/5 border-purple-600/30',
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color]} border p-3`}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-400">{title}</span>
        <div className={`text-${color}-500`}>{icon}</div>
      </div>
      <div className="text-xl font-bold">{value}</div>
    </div>
  );
}