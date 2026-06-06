import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Target, DollarSign, Calendar, AlertCircle, CheckCircle, Activity, RefreshCw } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const App = () => {
  const [activeTab, setActiveTab] = useState('extract');
  const [goalText, setGoalText] = useState('');
  const [extractedGoals, setExtractedGoals] = useState(null);
  const [simulationResults, setSimulationResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);

  // Goal form state
  const [goalForms, setGoalForms] = useState([{
    goal_id: 'goal_1',
    goal_name: 'Primary Goal',
    target_amount: 1000000,
    timeline_years: 20,
    current_savings: 50000,
    monthly_contribution: 2000,
    allocation: { stocks: 70, bonds: 25, cash: 5 }
  }]);

  const [simConfig, setSimConfig] = useState({
    num_simulations: 1000,
    confidence_level: 0.95,
    inflation_rate: 0.03,
    rebalancing_frequency: 'annually',
    use_historical_data: true,
    historical_years: 20
  });

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      const data = await res.json();
      setHealth(data);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const extractGoals = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/goals/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: goalText })
      });
      
      if (!res.ok) throw new Error('Failed to extract goals');
      
      const data = await res.json();
      setExtractedGoals(data);
      
      // Convert to simulation format
      if (data.goals && data.goals.length > 0) {
        const newForms = data.goals.map((g, i) => ({
          goal_id: `goal_${i + 1}`,
          goal_name: g.description || g.goal_type,
          target_amount: g.target_amount || 0,
          timeline_years: g.timeline_years || 10,
          current_savings: g.current_savings || 0,
          monthly_contribution: g.monthly_contribution || 1000,
          allocation: { 
            stocks: g.risk_tolerance === 'aggressive' ? 80 : g.risk_tolerance === 'conservative' ? 40 : 60,
            bonds: g.risk_tolerance === 'aggressive' ? 15 : g.risk_tolerance === 'conservative' ? 50 : 35,
            cash: 5
          }
        }));
        setGoalForms(newForms);
        setActiveTab('configure');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/simulation/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goals: goalForms,
          config: simConfig
        })
      });
      
      if (!res.ok) throw new Error('Simulation failed');
      
      const data = await res.json();
      setSimulationResults(data);
      setActiveTab('results');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateGoalForm = (index, field, value) => {
    const newForms = [...goalForms];
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      newForms[index][parent][child] = parseFloat(value) || 0;
    } else {
      newForms[index][field] = field.includes('amount') || field.includes('savings') || field.includes('contribution') || field.includes('years') 
        ? parseFloat(value) || 0 
        : value;
    }
    setGoalForms(newForms);
  };

  const addGoal = () => {
    setGoalForms([...goalForms, {
      goal_id: `goal_${goalForms.length + 1}`,
      goal_name: `Goal ${goalForms.length + 1}`,
      target_amount: 100000,
      timeline_years: 10,
      current_savings: 0,
      monthly_contribution: 500,
      allocation: { stocks: 60, bonds: 35, cash: 5 }
    }]);
  };

  const removeGoal = (index) => {
    if (goalForms.length > 1) {
      setGoalForms(goalForms.filter((_, i) => i !== index));
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercent = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Mycroft Goal Simulator</h1>
                <p className="text-sm text-slate-500">AI-Powered Investment Planning</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {health && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 rounded-lg">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-green-700">
                    {health.ollama?.available ? 'Ollama Connected' : 'Ollama Offline'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 mb-6">
          <div className="flex border-b border-slate-200">
            {['extract', 'configure', 'results'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                  activeTab === tab
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                {tab === 'extract' && '1. Extract Goals'}
                {tab === 'configure' && '2. Configure Simulation'}
                {tab === 'results' && '3. View Results'}
              </button>
            ))}
          </div>

          {/* Error Display */}
          {error && (
            <div className="mx-6 mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-red-900">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'extract' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 mb-4">Describe Your Goals</h2>
                  <p className="text-slate-600 mb-4">Tell us about your financial goals in natural language. Our AI will extract and structure them.</p>
                  
                  <textarea
                    value={goalText}
                    onChange={(e) => setGoalText(e.target.value)}
                    placeholder="Example: I want to retire in 20 years with $2M. I have $100k saved and can invest $3k monthly. I also want to save $50k for a house down payment in 5 years."
                    className="w-full h-40 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                </div>

                <button
                  onClick={extractGoals}
                  disabled={!goalText || loading}
                  className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Extracting Goals...
                    </>
                  ) : (
                    <>
                      <Activity className="w-5 h-5" />
                      Extract Goals with AI
                    </>
                  )}
                </button>

                {extractedGoals && (
                  <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-start gap-3 mb-4">
                      <CheckCircle className="w-6 h-6 text-green-600 mt-0.5" />
                      <div>
                        <h3 className="font-semibold text-green-900">Goals Extracted Successfully</h3>
                        <p className="text-sm text-green-700 mt-1">{extractedGoals.summary}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-4 mt-4">
                      {extractedGoals.goals.map((goal, i) => (
                        <div key={i} className="bg-white p-4 rounded-lg border border-green-200">
                          <div className="flex items-start justify-between mb-2">
                            <span className="font-medium text-slate-900 capitalize">{goal.goal_type}</span>
                            <span className="text-sm px-2 py-1 bg-blue-100 text-blue-700 rounded">
                              {formatPercent(goal.confidence_score)} confident
                            </span>
                          </div>
                          <p className="text-slate-600 text-sm mb-3">{goal.description}</p>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-slate-500">Target:</span>
                              <span className="ml-2 font-medium text-slate-900">{formatCurrency(goal.target_amount)}</span>
                            </div>
                            <div>
                              <span className="text-slate-500">Timeline:</span>
                              <span className="ml-2 font-medium text-slate-900">{goal.timeline_years} years</span>
                            </div>
                            <div>
                              <span className="text-slate-500">Risk:</span>
                              <span className="ml-2 font-medium text-slate-900 capitalize">{goal.risk_tolerance}</span>
                            </div>
                            <div>
                              <span className="text-slate-500">Priority:</span>
                              <span className="ml-2 font-medium text-slate-900 capitalize">{goal.priority}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    <button
                      onClick={() => setActiveTab('configure')}
                      className="w-full mt-4 px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Continue to Configuration →
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'configure' && (
              <div className="space-y-8">
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-slate-900">Configure Your Goals</h2>
                    <button
                      onClick={addGoal}
                      className="px-4 py-2 bg-blue-100 text-blue-700 font-medium rounded-lg hover:bg-blue-200 transition-colors"
                    >
                      + Add Goal
                    </button>
                  </div>

                  {goalForms.map((goal, index) => (
                    <div key={index} className="mb-6 p-6 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-slate-900">Goal {index + 1}</h3>
                        {goalForms.length > 1 && (
                          <button
                            onClick={() => removeGoal(index)}
                            className="text-red-600 hover:text-red-700 text-sm font-medium"
                          >
                            Remove
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Goal Name</label>
                          <input
                            type="text"
                            value={goal.goal_name}
                            onChange={(e) => updateGoalForm(index, 'goal_name', e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Target Amount ($)</label>
                          <input
                            type="number"
                            value={goal.target_amount}
                            onChange={(e) => updateGoalForm(index, 'target_amount', e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Timeline (years)</label>
                          <input
                            type="number"
                            value={goal.timeline_years}
                            onChange={(e) => updateGoalForm(index, 'timeline_years', e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Current Savings ($)</label>
                          <input
                            type="number"
                            value={goal.current_savings}
                            onChange={(e) => updateGoalForm(index, 'current_savings', e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Monthly Contribution ($)</label>
                          <input
                            type="number"
                            value={goal.monthly_contribution}
                            onChange={(e) => updateGoalForm(index, 'monthly_contribution', e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>

                      <div className="mt-4">
                        <label className="block text-sm font-medium text-slate-700 mb-3">Asset Allocation</label>
                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <label className="block text-xs text-slate-600 mb-1">Stocks (%)</label>
                            <input
                              type="number"
                              min="0"
                              max="100"
                              value={goal.allocation.stocks}
                              onChange={(e) => updateGoalForm(index, 'allocation.stocks', e.target.value)}
                              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-slate-600 mb-1">Bonds (%)</label>
                            <input
                              type="number"
                              min="0"
                              max="100"
                              value={goal.allocation.bonds}
                              onChange={(e) => updateGoalForm(index, 'allocation.bonds', e.target.value)}
                              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-slate-600 mb-1">Cash (%)</label>
                            <input
                              type="number"
                              min="0"
                              max="100"
                              value={goal.allocation.cash}
                              onChange={(e) => updateGoalForm(index, 'allocation.cash', e.target.value)}
                              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            />
                          </div>
                        </div>
                        <p className="text-xs text-slate-500 mt-2">
                          Total: {goal.allocation.stocks + goal.allocation.bonds + goal.allocation.cash}%
                          {goal.allocation.stocks + goal.allocation.bonds + goal.allocation.cash !== 100 && (
                            <span className="text-red-600 ml-2">Must equal 100%</span>
                          )}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
                  <h3 className="text-lg font-medium text-slate-900 mb-4">Simulation Configuration</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">Number of Simulations</label>
                      <input
                        type="number"
                        value={simConfig.num_simulations}
                        onChange={(e) => setSimConfig({...simConfig, num_simulations: parseInt(e.target.value)})}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">Inflation Rate</label>
                      <input
                        type="number"
                        step="0.01"
                        value={simConfig.inflation_rate}
                        onChange={(e) => setSimConfig({...simConfig, inflation_rate: parseFloat(e.target.value)})}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>

                <button
                  onClick={runSimulation}
                  disabled={loading || goalForms.some(g => g.allocation.stocks + g.allocation.bonds + g.allocation.cash !== 100)}
                  className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:from-slate-300 disabled:to-slate-300 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Running {simConfig.num_simulations} Simulations...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-5 h-5" />
                      Run Monte Carlo Simulation
                    </>
                  )}
                </button>
              </div>
            )}

            {activeTab === 'results' && simulationResults && (
              <div className="space-y-6">
                <div className="grid grid-cols-3 gap-6">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                        <Target className="w-5 h-5 text-white" />
                      </div>
                      <span className="text-sm font-medium text-slate-600">Success Rate</span>
                    </div>
                    <p className="text-3xl font-bold text-slate-900">
                      {formatPercent(simulationResults.total_success_probability)}
                    </p>
                  </div>

                  <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border border-green-200">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                        <DollarSign className="w-5 h-5 text-white" />
                      </div>
                      <span className="text-sm font-medium text-slate-600">Total Target</span>
                    </div>
                    <p className="text-3xl font-bold text-slate-900">
                      {formatCurrency(simulationResults.portfolio_statistics.total_target_amount)}
                    </p>
                  </div>

                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                        <Calendar className="w-5 h-5 text-white" />
                      </div>
                      <span className="text-sm font-medium text-slate-600">Monthly Investment</span>
                    </div>
                    <p className="text-3xl font-bold text-slate-900">
                      {formatCurrency(simulationResults.portfolio_statistics.total_monthly_contribution)}
                    </p>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-xl border border-slate-200">
                  <h3 className="text-lg font-semibold text-slate-900 mb-4">Overall Recommendations</h3>
                  <div className="space-y-2">
                    {simulationResults.recommendations.map((rec, i) => (
                      <div key={i} className={`p-3 rounded-lg ${rec.includes('✅') ? 'bg-green-50 text-green-800' : 'bg-amber-50 text-amber-800'}`}>
                        {rec}
                      </div>
                    ))}
                  </div>
                </div>

                {simulationResults.goals.map((goal, idx) => (
                  <div key={idx} className="bg-white p-6 rounded-xl border border-slate-200">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h3 className="text-xl font-semibold text-slate-900">{goal.goal_name}</h3>
                        <p className="text-sm text-slate-500 mt-1">Goal ID: {goal.goal_id}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-blue-600">
                          {formatPercent(goal.success_probability)}
                        </div>
                        <div className="text-sm text-slate-500">Success Rate</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-4 gap-4 mb-6">
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-xs text-slate-600 mb-1">Median Outcome</div>
                        <div className="text-lg font-semibold text-slate-900">
                          {formatCurrency(goal.median_outcome)}
                        </div>
                      </div>
                      <div className="p-4 bg-red-50 rounded-lg">
                        <div className="text-xs text-red-600 mb-1">Worst Case (10th)</div>
                        <div className="text-lg font-semibold text-red-900">
                          {formatCurrency(goal.worst_case_10th)}
                        </div>
                      </div>
                      <div className="p-4 bg-green-50 rounded-lg">
                        <div className="text-xs text-green-600 mb-1">Best Case (90th)</div>
                        <div className="text-lg font-semibold text-green-900">
                          {formatCurrency(goal.best_case_90th)}
                        </div>
                      </div>
                      <div className="p-4 bg-amber-50 rounded-lg">
                        <div className="text-xs text-amber-600 mb-1">Expected Shortfall</div>
                        <div className="text-lg font-semibold text-amber-900">
                          {formatCurrency(goal.expected_shortfall)}
                        </div>
                      </div>
                    </div>

                    <div className="mb-6">
                      <h4 className="text-sm font-medium text-slate-700 mb-3">Outcome Distribution</h4>
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={Object.entries(goal.percentile_outcomes).map(([k, v]) => ({
                          percentile: k.replace('p', '') + 'th',
                          amount: v
                        }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="percentile" />
                          <YAxis tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                          <Tooltip formatter={(v) => formatCurrency(v)} />
                          <Bar dataKey="amount" fill="#3b82f6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {goal.recommended_adjustments.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-slate-700 mb-2">Recommendations</h4>
                        <div className="space-y-2">
                          {goal.recommended_adjustments.map((adj, i) => (
                            <div key={i} className={`p-3 rounded-lg text-sm ${
                              adj.includes('✅') ? 'bg-green-50 text-green-800' : 
                              adj.includes('⚠️') ? 'bg-amber-50 text-amber-800' : 
                              'bg-blue-50 text-blue-800'
                            }`}>
                              {adj}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                <div className="flex gap-4">
                  <button
                    onClick={() => setActiveTab('configure')}
                    className="flex-1 px-6 py-3 bg-slate-100 text-slate-700 font-medium rounded-lg hover:bg-slate-200 transition-colors"
                  >
                    ← Modify Configuration
                  </button>
                  <button
                    onClick={runSimulation}
                    disabled={loading}
                    className="flex-1 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-slate-300 transition-colors flex items-center justify-center gap-2"
                  >
                    <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    Re-run Simulation
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'results' && !simulationResults && (
              <div className="text-center py-12">
                <Activity className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-slate-600 mb-2">No Simulation Results Yet</h3>
                <p className="text-slate-500">Configure your goals and run a simulation to see results here.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;