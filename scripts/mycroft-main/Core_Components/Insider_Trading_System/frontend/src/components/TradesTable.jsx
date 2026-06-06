import React, { useState } from 'react';
import { Activity, CheckCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import AnalysisDetails from './AnalysisDetails';

export default function TradesTable({ trades, analysesMap }) {
  const [expandedId, setExpandedId] = useState(null);

  if (trades.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 p-12 text-center">
        <Activity className="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <p className="text-gray-400">No trades found</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 border border-gray-800">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-800/50 border-b border-gray-800">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Politician</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Ticker</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Type</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider"></th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => {
              const analysis = analysesMap[trade.trade_id];
              const isExpanded = expandedId === trade.id;
              
              return (
                <React.Fragment key={trade.id}>
                  <tr className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
                    <td className="px-4 py-2">
                      <div className="flex items-center space-x-2">
                        <div className="text-sm font-medium text-gray-100">{trade.politician}</div>
                        <span className={`px-1.5 py-0.5 text-xs ${
                          trade.party === 'Republican' 
                            ? 'bg-red-900/30 text-red-400 border border-red-800/50'
                            : trade.party === 'Democrat'
                            ? 'bg-blue-900/30 text-blue-400 border border-blue-800/50'
                            : 'bg-gray-700/30 text-gray-400 border border-gray-600/50'
                        }`}>
                          {trade.party === 'Republican' ? 'R' : trade.party === 'Democrat' ? 'D' : '?'}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-2">
                      <span className="text-sm font-mono text-blue-400">{trade.trade_ticker}</span>
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
                          onClick={() => setExpandedId(isExpanded ? null : trade.id)}
                          className="text-gray-400 hover:text-gray-300 text-xs flex items-center space-x-1"
                        >
                          <span>{isExpanded ? 'Hide' : 'View'}</span>
                          {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        </button>
                      )}
                    </td>
                  </tr>
                  {isExpanded && analysis && !analysis.error && (
                    <tr>
                      <td colSpan="7" className="p-0">
                        <AnalysisDetails analysis={analysis} />
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}