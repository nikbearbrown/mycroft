import pandas as pd
import re
from datetime import date
from models import Trade

# ── Broker detection ────────────────────────────────────────────────────────

BROKER_SIGNATURES = {
    "robinhood": {"Activity Date", "Instrument", "Trans Code", "Quantity", "Price"},
    "ibkr":      {"TradeDate", "Symbol", "Buy/Sell", "Quantity", "TradePrice"},
    "schwab":    {"Date", "Action", "Symbol", "Quantity", "Price"},
    "fidelity":  {"Trade Date", "Action", "Symbol", "Quantity", "Price ($)"},
}

def detect_broker(cols: set) -> str:
    for broker, sig in BROKER_SIGNATURES.items():
        if sig.issubset(cols):
            return broker
    return "unknown"


# ── Per-broker normalization ─────────────────────────────────────────────────

def _norm_robinhood(df: pd.DataFrame) -> pd.DataFrame:
    action_map = {"Buy": "BUY", "Sell": "SELL", "STO": "SELL", "BTO": "BUY"}
    df = df[df["Trans Code"].isin(action_map)].copy()
    df["action"]   = df["Trans Code"].map(action_map)
    df["date"]     = pd.to_datetime(df["Activity Date"]).dt.date
    df["ticker"]   = df["Instrument"].str.strip()
    df["quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").abs()
    df["price"]    = pd.to_numeric(df["Price"].replace(r'[\$,]', '', regex=True), errors="coerce")
    df["amount"]   = df.apply(lambda r: -r.quantity * r.price if r.action == "BUY" else r.quantity * r.price, axis=1)
    df["broker"]   = "robinhood"
    return df[["date", "ticker", "action", "quantity", "price", "amount", "broker"]]


def _norm_ibkr(df: pd.DataFrame) -> pd.DataFrame:
    action_map = {"BUY": "BUY", "SELL": "SELL"}
    df = df[df["Buy/Sell"].isin(action_map)].copy()
    df["action"]   = df["Buy/Sell"].map(action_map)
    df["date"]     = pd.to_datetime(df["TradeDate"]).dt.date
    df["ticker"]   = df["Symbol"].str.strip()
    df["quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").abs()
    df["price"]    = pd.to_numeric(df["TradePrice"], errors="coerce")
    df["amount"]   = df.apply(lambda r: -r.quantity * r.price if r.action == "BUY" else r.quantity * r.price, axis=1)
    df["broker"]   = "ibkr"
    return df[["date", "ticker", "action", "quantity", "price", "amount", "broker"]]


def _norm_schwab(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["action_raw"] = df["Action"].str.strip().str.lower()
    df = df[df["action_raw"].str.contains("buy|sell")].copy()
    df["action"]   = df["action_raw"].apply(lambda x: "BUY" if "buy" in x else "SELL")
    df["date"]     = pd.to_datetime(df["Date"]).dt.date
    df["ticker"]   = df["Symbol"].str.strip()
    df["quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").abs()
    df["price"]    = pd.to_numeric(df["Price"].replace(r'[\$,]', '', regex=True), errors="coerce")
    df["amount"]   = df.apply(lambda r: -r.quantity * r.price if r.action == "BUY" else r.quantity * r.price, axis=1)
    df["broker"]   = "schwab"
    return df[["date", "ticker", "action", "quantity", "price", "amount", "broker"]]


def _norm_fidelity(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["action_raw"] = df["Action"].str.strip().str.lower()
    df = df[df["action_raw"].str.contains("bought|sold")].copy()
    df["action"]   = df["action_raw"].apply(lambda x: "BUY" if "bought" in x else "SELL")
    df["date"]     = pd.to_datetime(df["Trade Date"]).dt.date
    df["ticker"]   = df["Symbol"].str.strip()
    df["quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").abs()
    df["price"]    = pd.to_numeric(df["Price ($)"].replace(r'[\$,]', '', regex=True), errors="coerce")
    df["amount"]   = df.apply(lambda r: -r.quantity * r.price if r.action == "BUY" else r.quantity * r.price, axis=1)
    df["broker"]   = "fidelity"
    return df[["date", "ticker", "action", "quantity", "price", "amount", "broker"]]


NORMALIZERS = {
    "robinhood": _norm_robinhood,
    "ibkr":      _norm_ibkr,
    "schwab":    _norm_schwab,
    "fidelity":  _norm_fidelity,
}


# ── P&L matching (FIFO) ──────────────────────────────────────────────────────

def compute_pnl(df: pd.DataFrame) -> pd.DataFrame:
    """
    FIFO cost-basis matching.
    Adds: days_held, pnl, pnl_pct, is_winner to SELL rows.
    """
    df = df.sort_values("date").copy()
    df["days_held"] = None
    df["pnl"]       = None
    df["pnl_pct"]   = None
    df["is_winner"] = None

    # Queue: ticker -> list of (date, price, qty) for open lots
    lots: dict[str, list] = {}

    for idx, row in df.iterrows():
        ticker = row["ticker"]
        if row["action"] == "BUY":
            lots.setdefault(ticker, []).append({
                "date": row["date"], "price": row["price"], "qty": row["quantity"]
            })
        elif row["action"] == "SELL":
            sell_qty   = row["quantity"]
            sell_price = row["price"]
            sell_date  = row["date"]
            cost_basis = 0.0
            total_days = 0.0
            matched_qty = 0.0

            queue = lots.get(ticker, [])
            while sell_qty > 0 and queue:
                lot = queue[0]
                take = min(lot["qty"], sell_qty)
                cost_basis  += take * lot["price"]
                total_days  += take * (sell_date - lot["date"]).days
                matched_qty += take
                lot["qty"]  -= take
                sell_qty    -= take
                if lot["qty"] <= 0:
                    queue.pop(0)

            if matched_qty > 0:
                avg_cost  = cost_basis / matched_qty
                pnl       = (sell_price - avg_cost) * matched_qty
                pnl_pct   = (sell_price - avg_cost) / avg_cost * 100
                avg_days  = total_days / matched_qty

                df.at[idx, "days_held"] = round(avg_days)
                df.at[idx, "pnl"]       = round(pnl, 2)
                df.at[idx, "pnl_pct"]   = round(pnl_pct, 2)
                df.at[idx, "is_winner"] = pnl > 0

    return df


# ── Public interface ─────────────────────────────────────────────────────────

def parse_csv(filepath: str) -> tuple[list[Trade], str]:
    """
    Parse a brokerage CSV into a list of Trade objects.
    Returns (trades, broker_name).
    Raises ValueError on unknown format.
    """
    raw = pd.read_csv(filepath)
    cols = set(raw.columns.str.strip())
    broker = detect_broker(cols)

    if broker == "unknown":
        raise ValueError(
            f"Unrecognized CSV format. Detected columns: {cols}. "
            "Supported brokers: Robinhood, IBKR, Schwab, Fidelity."
        )

    norm_fn = NORMALIZERS[broker]
    df = norm_fn(raw)
    df = df.dropna(subset=["date", "ticker", "quantity", "price"])
    df = compute_pnl(df)
    df = df.sort_values("date")

    trades = [
        Trade(
            date=row["date"],
            ticker=row["ticker"],
            action=row["action"],
            quantity=row["quantity"],
            price=row["price"],
            amount=row["amount"],
            broker=broker,
        )
        for _, row in df.iterrows()
    ]
    return trades, broker


def parse_csv_to_df(filepath: str) -> tuple[pd.DataFrame, str]:
    """Same as parse_csv but returns the enriched DataFrame directly (used by enricher)."""
    raw = pd.read_csv(filepath)
    cols = set(raw.columns.str.strip())
    broker = detect_broker(cols)

    if broker == "unknown":
        raise ValueError(f"Unrecognized CSV format. Columns: {cols}")

    df = NORMALIZERS[broker](raw)
    df = df.dropna(subset=["date", "ticker", "quantity", "price"])
    df = compute_pnl(df)
    # Cast P&L columns from object → numeric after FIFO assignment
    for col in ["pnl", "pnl_pct", "days_held"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["is_winner"] = df["is_winner"].astype("boolean")

    return df.sort_values("date").reset_index(drop=True), broker