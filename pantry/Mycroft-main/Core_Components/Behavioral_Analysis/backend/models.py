from pydantic import BaseModel
from typing import Optional
from datetime import date


class Trade(BaseModel):
    date: date
    ticker: str
    action: str           # BUY or SELL
    quantity: float
    price: float
    amount: float         # quantity * price (signed: negative = buy, positive = sell)
    broker: Optional[str] = None


class EnrichedTrade(Trade):
    # yfinance enrichment
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[str] = None      # large / mid / small / micro
    market_cap_raw: Optional[float] = None

    # Computed per trade
    days_held: Optional[int] = None
    pnl: Optional[float] = None           # realized P&L (on SELL trades)
    pnl_pct: Optional[float] = None
    is_winner: Optional[bool] = None

    # FRED macro context at trade date
    vix_level: Optional[float] = None
    vix_regime: Optional[str] = None      # low / elevated / high / extreme
    fed_funds_rate: Optional[float] = None
    in_recession: Optional[bool] = None
    market_regime: Optional[str] = None   # bull / bear / choppy

    # Earnings proximity
    days_to_earnings: Optional[int] = None
    earnings_trade: Optional[bool] = None  # within 5 days of earnings


class TradeStats(BaseModel):
    total_trades: int
    total_buys: int
    total_sells: int
    unique_tickers: int
    date_range_start: date
    date_range_end: date
    total_realized_pnl: float
    win_rate: float
    avg_hold_days: float


class AgentFindings(BaseModel):
    agent_name: str
    summary: str
    metrics: dict
    insights: list[str]
    edge_score: Optional[float] = None    # -1 to 1, where 1 = strong edge


class EdgeReport(BaseModel):
    trade_stats: TradeStats
    agent_findings: list[AgentFindings]
    narrative: str                         # Claude-written verdict
    edge_profile: dict                     # structured summary of where edge exists
    generated_at: str