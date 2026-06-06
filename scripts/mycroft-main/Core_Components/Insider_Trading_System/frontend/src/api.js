const API_BASE = 'http://localhost:8000';

export const fetchStats = async () => {
  const res = await fetch(`${API_BASE}/stats`);
  return res.json();
};

export const fetchTrades = async () => {
  const res = await fetch(`${API_BASE}/trades?limit=100`);
  return res.json();
};

export const fetchAnalyses = async () => {
  const res = await fetch(`${API_BASE}/analyses?limit=100`);
  return res.json();
};

export const startScrape = async () => {
  await fetch(`${API_BASE}/scrape`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recent_days: 45, min_trade_size: 5000, pages: 7 })
  });
};

export const startAnalysis = async () => {
  await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ days_before: 30, days_after: 30 })
  });
};