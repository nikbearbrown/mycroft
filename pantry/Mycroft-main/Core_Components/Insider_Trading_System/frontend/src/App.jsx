import React, { useState, useEffect } from 'react';
import { Activity, RefreshCw, Search, Filter, BarChart3 } from 'lucide-react';
import { fetchStats, fetchTrades, fetchAnalyses, startScrape, startAnalysis } from './api';
import StatsCards from './components/StatsCards';
import TradesTable from './components/TradesTable';
import PoliticiansView from './components/PoliticiansView';

export default function CongressionalTradingDashboard() {
  const [stats, setStats] = useState(null);
  const [trades, setTrades] = useState([]);
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('trades');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [scraping, setScraping] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, tradesData, analysesData] = await Promise.all([
        fetchStats(),
        fetchTrades(),
        fetchAnalyses()
      ]);
      setStats(statsData);
      setTrades(tradesData);
      setAnalyses(analysesData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScrape = async () => {
    setScraping(true);
    try {
      await startScrape();
      setTimeout(() => {
        loadData();
        setScraping(false);
      }, 5000);
    } catch (error) {
      console.error('Error scraping:', error);
      setScraping(false);
    }
  };

  const handleAnalysis = async () => {
    setAnalyzing(true);
    try {
      await startAnalysis();
      setTimeout(() => {
        loadData();
        setAnalyzing(false);
      }, 5000);
    } catch (error) {
      console.error('Error analyzing:', error);
      setAnalyzing(false);
    }
  };

  // Create analyses map
  const analysesMap = analyses.reduce((acc, analysis) => {
    acc[analysis.trade_id] = analysis;
    return acc;
  }, {});

  // Filter trades
  const filteredTrades = trades.filter(trade => {
    const matchesSearch = trade.politician.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         trade.trade_ticker.toLowerCase().includes(searchTerm.toLowerCase());
    
    let matchesFilter = true;
    if (filterType === 'buy') {
      matchesFilter = trade.transaction_type?.toLowerCase().includes('purchase') || 
                     trade.transaction_type?.toLowerCase().includes('buy');
    } else if (filterType === 'sell') {
      matchesFilter = !(trade.transaction_type?.toLowerCase().includes('purchase') || 
                       trade.transaction_type?.toLowerCase().includes('buy'));
    }
    
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Activity className="w-7 h-7 text-blue-500" />
              <div>
                <h1 className="text-xl font-bold text-gray-100">Congressional Trading Monitor</h1>
                <p className="text-xs text-gray-400">Track and analyze congressional stock trades</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleScrape}
                disabled={scraping}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-sm flex items-center space-x-2 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
                <span>{scraping ? 'Scraping...' : 'Scrape'}</span>
              </button>
              <button
                onClick={handleAnalysis}
                disabled={analyzing}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 text-sm flex items-center space-x-2 transition-colors"
              >
                <BarChart3 className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
                <span>{analyzing ? 'Analyzing...' : 'Analyze'}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Stats Cards */}
        {stats && <StatsCards stats={stats} />}

        {/* Search and Filter Bar */}
        <div className="bg-gray-900 p-3 mb-4 border border-gray-800">
          <div className="flex gap-3 items-center">
            {/* Tabs */}
            <div className="flex border-r border-gray-700 pr-3">
              <button
                onClick={() => setActiveTab('trades')}
                className={`px-3 py-1 text-sm ${
                  activeTab === 'trades'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                Trades
              </button>
              <button
                onClick={() => setActiveTab('politicians')}
                className={`px-3 py-1 text-sm ${
                  activeTab === 'politicians'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                Politicians
              </button>
            </div>

            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder={activeTab === 'trades' ? "Search by politician or ticker..." : "Search politicians..."}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-gray-800 border border-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm text-gray-100"
              />
            </div>
            
            {activeTab === 'trades' && (
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-3 py-2 bg-gray-800 border border-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm text-gray-100"
                >
                  <option value="all">All</option>
                  <option value="buy">Buy</option>
                  <option value="sell">Sell</option>
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : activeTab === 'trades' ? (
          <TradesTable trades={filteredTrades} analysesMap={analysesMap} />
        ) : (
          <PoliticiansView trades={trades} analysesMap={analysesMap} searchTerm={searchTerm} />
        )}
      </div>
    </div>
  );
}