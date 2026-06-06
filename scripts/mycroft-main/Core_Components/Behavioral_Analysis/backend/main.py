import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from parser import parse_csv_to_df
from enricher import enrich
from graph import run_analysis
from models import EdgeReport

app = FastAPI(title="Behavioral Alpha API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=EdgeReport)
async def analyze(file: UploadFile = File(...)):
    """
    Upload a brokerage CSV. Returns a full EdgeReport.
    Supported brokers: Robinhood, IBKR, Schwab, Fidelity.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # Save upload to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # 1. Parse
        df, broker = parse_csv_to_df(tmp_path)
        if df.empty:
            raise HTTPException(status_code=422, detail="No valid trades found in CSV.")

        # 2. Enrich
        enriched = enrich(df)

        # 3. Run LangGraph analysis
        report = run_analysis(enriched)

        return report

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        os.unlink(tmp_path)


@app.post("/parse-preview")
async def parse_preview(file: UploadFile = File(...)):
    """
    Lightweight endpoint: parse + detect broker without running full analysis.
    Useful for validating the file before committing to the full run.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        df, broker = parse_csv_to_df(tmp_path)
        sells = df[(df["action"] == "SELL") & df["pnl"].notna()]
        return {
            "broker":        broker,
            "total_trades":  len(df),
            "unique_tickers":df["ticker"].nunique(),
            "date_range":    {"start": str(df["date"].min()), "end": str(df["date"].max())},
            "closed_trades": len(sells),
            "sample_tickers":df["ticker"].value_counts().head(5).index.tolist(),
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        os.unlink(tmp_path)