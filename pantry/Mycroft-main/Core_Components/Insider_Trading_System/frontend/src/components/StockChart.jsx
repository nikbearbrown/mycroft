import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function StockChart({ chartData, ticker, politician, transactionType }) {
  if (!chartData || !chartData.dates || chartData.dates.length === 0) {
    return (
      <div className="p-4 bg-gray-800/50 text-center text-gray-400 text-sm">
        No chart data available
      </div>
    );
  }

  const priceData = chartData.dates.map((date, idx) => ({
    date: date,
    price: chartData.close_prices[idx],
    isTradeDate: idx === chartData.trade_date_index
  }));

  const volumeData = chartData.dates.map((date, idx) => ({
    date: date,
    volume: chartData.volumes[idx],
    isUp: chartData.close_prices[idx] >= chartData.open_prices[idx]
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-700 p-2 shadow-lg">
          <p className="text-xs text-gray-300">{payload[0].payload.date}</p>
          <p className="text-xs font-semibold text-blue-400">
            ${payload[0].value.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  const VolumeTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-700 p-2 shadow-lg">
          <p className="text-xs text-gray-300">{payload[0].payload.date}</p>
          <p className="text-xs font-semibold text-purple-400">
            {(payload[0].value / 1000000).toFixed(2)}M
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="p-4 bg-gray-800/30">
      <div className="mb-3">
        <h4 className="text-sm font-semibold text-gray-100">
          {ticker} • {politician} • {transactionType}
        </h4>
        <p className="text-xs text-gray-400">Trade Date: {chartData.trade_date}</p>
      </div>

      {/* Price Chart */}
      <div className="mb-4">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={priceData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF', fontSize: 10 }}
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <YAxis 
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF', fontSize: 10 }}
              domain={['auto', 'auto']}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine 
              x={chartData.trade_date} 
              stroke="#EF4444" 
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{ value: 'Trade', position: 'top', fill: '#EF4444', fontSize: 10 }}
            />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#3B82F6" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#3B82F6' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Volume Chart */}
      <div>
        <ResponsiveContainer width="100%" height={120}>
          <BarChart data={volumeData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF', fontSize: 10 }}
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <YAxis 
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF', fontSize: 10 }}
              tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
            />
            <Tooltip content={<VolumeTooltip />} />
            <ReferenceLine 
              x={chartData.trade_date} 
              stroke="#EF4444" 
              strokeWidth={2}
              strokeDasharray="5 5"
            />
            <Bar 
              dataKey="volume" 
              fill="#8B5CF6"
              opacity={0.6}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}