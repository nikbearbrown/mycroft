import { TrendingUp, AlertCircle, FileText, Zap } from 'lucide-react';

export default function Stats({ stats, selectedCount }) {
  if (!stats) {
    return (
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-gray-100 h-24 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  const urgency = stats.urgency_distribution || {};

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard
        icon={<FileText className="w-6 h-6 text-blue-600" />}
        label="Total Feeds"
        value={stats.total_feeds || 0}
        color="bg-blue-50"
      />
      <StatCard
        icon={<AlertCircle className="w-6 h-6 text-red-600" />}
        label="Critical"
        value={urgency.critical || 0}
        color="bg-red-50"
      />
      <StatCard
        icon={<TrendingUp className="w-6 h-6 text-orange-600" />}
        label="High Priority"
        value={urgency.high || 0}
        color="bg-orange-50"
      />
      <StatCard
        icon={<Zap className="w-6 h-6 text-purple-600" />}
        label="Selected"
        value={selectedCount}
        color="bg-purple-50"
      />
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className={`${color} rounded-lg p-4 flex items-center gap-3`}>
      <div>{icon}</div>
      <div>
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className="text-sm text-gray-600">{label}</div>
      </div>
    </div>
  );
}