import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, AlertCircle } from 'lucide-react';
import AnalysisDetails from './AnalysisDetails';

export default function PoliticianCard({ politician, analysesMap, expanded, onToggle }) {
  return (
    <div className="border-b border-gray-800 last:border-b-0">
      <div 
        className="px-4 py-3 hover:bg-gray-800/30 cursor-pointer flex items-center justify-between"
        onClick={onToggle}
      >
        <div className="flex items-center space-x-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-100">{politician.name}</span>
              <span className={`px-1.5 py-0.5 text-xs ${
                politician.party === 'Republican' 
                  ? 'bg-red-900/30 text-red-400 border border-red-800/50'
                  : politician.party === 'Democrat'
                  ? 'bg-blue-900/30 text-blue-400 border border-blue-800/50'
                  : 'bg-gray-700/30 text-gray-400 border border-gray-600/50'
              }`}>
                {politician.party}
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-1">
              {politician.totalTrades} trades • {politician.analyzedTrades} analyzed
              {politician.totalValue > 0 && ` • Min Total: ${(politician.totalValue / 1000).toFixed(0)}K`}
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500">
            {expanded ? 'Hide' : 'View'} Trades
          </span>
          {expanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
        </div>
      </div>

      {expanded && (
        <div className="bg-gray-800/30">
          <table className="w-full">
            <thead className="bg-gray-800/50 border-t border-b border-gray-700">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Date</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Ticker</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Type</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Size</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Filed</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody>
              {politician.trades.map((trade) => (
                <TradeRow 
                  key={trade.id} 
                  trade={trade} 
                  analysis={analysesMap[trade.trade_id]} 
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function TradeRow({ trade, analysis }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <tr className="border-b border-gray-700 hover:bg-gray-800/50">
        <td className="px-4 py-2 text-xs text-gray-300">{trade.traded_date}</td>
        <td className="px-4 py-2">
          <span className="text-xs font-mono text-blue-400">{trade.trade_ticker}</span>
        </td>
        <td className="px-4 py-2">
          <span className={`px-2 py-0.5 text-xs ${
            trade.transaction_type?.toLowerCase().includes('purchase') || 
            trade.transaction_type?.toLowerCase().includes('buy')
              ? 'bg-green-900/30 text-green-400 border border-green-800/50'
              : 'bg-red-900/30 text-red-400 border border-red-800/50'
          }`}>
            {trade.transaction_type?.toLowerCase().includes('purchase') || 
             trade.transaction_type?.toLowerCase().includes('buy') ? 'BUY' : 'SELL'}
          </span>
        </td>
        <td className="px-4 py-2 text-xs text-gray-300">
          {trade.trade_size_min !== null && trade.trade_size_min !== undefined ? (
            trade.trade_size_max !== null && trade.trade_size_max !== undefined 
              ? `${(trade.trade_size_min/1000).toFixed(0)}K-${(trade.trade_size_max/1000).toFixed(0)}K`
              : `${(trade.trade_size_min/1000).toFixed(0)}K+`
          ) : 'N/A'}
        </td>
        <td className="px-4 py-2">
          {trade.filed_after !== null && trade.filed_after !== undefined ? (
            <span className={`px-2 py-0.5 text-xs ${
              trade.filed_after > 30
                ? 'bg-red-900/30 text-red-400 border border-red-800/50'
                : 'bg-green-900/30 text-green-400 border border-green-800/50'
            }`}>
              {trade.filed_after}d
            </span>
          ) : (
            <span className="text-xs text-gray-500">N/A</span>
          )}
        </td>
        <td className="px-4 py-2">
          {trade.analyzed ? (
            <CheckCircle className="w-4 h-4 text-green-500" />
          ) : (
            <AlertCircle className="w-4 h-4 text-yellow-500" />
          )}
        </td>
        <td className="px-4 py-2">
          {analysis && !analysis.error && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
              className="text-gray-400 hover:text-gray-300 text-xs flex items-center space-x-1"
            >
              <span>{expanded ? 'Hide' : 'View'}</span>
              {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          )}
        </td>
      </tr>
      {expanded && analysis && !analysis.error && (
        <tr>
          <td colSpan="7" className="p-0">
            <AnalysisDetails analysis={analysis} />
          </td>
        </tr>
      )}
    </>
  );
}