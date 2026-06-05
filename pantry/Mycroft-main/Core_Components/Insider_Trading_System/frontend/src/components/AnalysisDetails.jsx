import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import StockChart from './StockChart';

export default function AnalysisDetails({ analysis }) {
  return (
    <div className="bg-gray-800/50 border-t border-gray-700">
      {/* Metrics */}
      {analysis.metrics && Object.keys(analysis.metrics).length > 0 && (
        <div className="px-4 py-3 grid grid-cols-4 gap-3 border-b border-gray-700">
          {analysis.metrics.trade_price && (
            <MetricBox label="Trade Price" value={`$${analysis.metrics.trade_price}`} color="blue" />
          )}
          {analysis.metrics.change_to_trade !== undefined && (
            <MetricBox
              label="Pre-Trade (30d)"
              value={`${analysis.metrics.change_to_trade > 0 ? '+' : ''}${analysis.metrics.change_to_trade}%`}
              color={analysis.metrics.change_to_trade > 0 ? 'green' : 'red'}
              icon={analysis.metrics.change_to_trade > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            />
          )}
          {analysis.metrics.change_after_trade !== undefined && (
            <MetricBox
              label="Post-Trade (30d)"
              value={`${analysis.metrics.change_after_trade > 0 ? '+' : ''}${analysis.metrics.change_after_trade}%`}
              color={analysis.metrics.change_after_trade > 0 ? 'green' : 'red'}
              icon={analysis.metrics.change_after_trade > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            />
          )}
          {analysis.metrics.volatility && (
            <MetricBox label="Volatility" value={`${analysis.metrics.volatility}%`} color="purple" />
          )}
        </div>
      )}

      {/* Chart */}
      {analysis.chart_data && (
        <StockChart 
          chartData={analysis.chart_data} 
          ticker={analysis.ticker}
          politician={analysis.politician}
          transactionType={analysis.transaction_type}
        />
      )}
    </div>
  );
}

function MetricBox({ label, value, color, icon }) {
  const colors = {
    blue: 'bg-blue-900/20 border-blue-800/30 text-blue-400',
    green: 'bg-green-900/20 border-green-800/30 text-green-400',
    red: 'bg-red-900/20 border-red-800/30 text-red-400',
    purple: 'bg-purple-900/20 border-purple-800/30 text-purple-400',
  };

  return (
    <div className={`${colors[color]} border p-2`}>
      <div className="text-xs text-gray-400 mb-0.5">{label}</div>
      <div className="flex items-center space-x-1">
        {icon}
        <div className="text-base font-semibold">{value}</div>
      </div>
    </div>
  );
}