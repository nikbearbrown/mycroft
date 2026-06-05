import React, { useState } from 'react';
import { Activity, ChevronDown, ChevronUp } from 'lucide-react';
import PoliticianCard from './PoliticianCard';

export default function PoliticiansView({ trades, analysesMap, searchTerm }) {
  const [expandedPolitician, setExpandedPolitician] = useState(null);

  // Group trades by politician
  const politiciansData = trades.reduce((acc, trade) => {
    if (!acc[trade.politician]) {
      acc[trade.politician] = {
        name: trade.politician,
        party: trade.party,
        trades: [],
        totalTrades: 0,
        analyzedTrades: 0,
        totalValue: 0
      };
    }
    acc[trade.politician].trades.push(trade);
    acc[trade.politician].totalTrades++;
    if (trade.analyzed) acc[trade.politician].analyzedTrades++;
    if (trade.trade_size_min) acc[trade.politician].totalValue += trade.trade_size_min;
    return acc;
  }, {});

  // Convert to array and filter by search
  const politicians = Object.values(politiciansData)
    .filter(p => p.name.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => b.totalTrades - a.totalTrades);

  if (politicians.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 p-12 text-center">
        <Activity className="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <p className="text-gray-400">No politicians found</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 border border-gray-800">
      {politicians.map((politician) => (
        <PoliticianCard
          key={politician.name}
          politician={politician}
          analysesMap={analysesMap}
          expanded={expandedPolitician === politician.name}
          onToggle={() => setExpandedPolitician(
            expandedPolitician === politician.name ? null : politician.name
          )}
        />
      ))}
    </div>
  );
}