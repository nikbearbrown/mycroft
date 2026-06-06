from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import logging

from database import Trade, Analysis, get_db, init_db
from scraper import CapitolTradesScraperSelenium, Config as ScraperConfig
from analyzer import StockPriceAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Congressional Trading API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Pydantic models
class TradeResponse(BaseModel):
    id: int
    trade_id: str
    politician: str
    party: str
    trade_ticker: str
    transaction_type: str
    traded_date: str
    analyzed: bool
    
    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    id: int
    trade_id: str
    ticker: str
    politician: str
    transaction_type: str
    metrics: dict
    chart_data: Optional[dict]
    analyzed_at: datetime
    error: Optional[str]
    
    class Config:
        from_attributes = True

class ScrapeRequest(BaseModel):
    recent_days: int = 45
    min_trade_size: int = 5000
    pages: int = 7

class AnalyzeRequest(BaseModel):
    trade_ids: Optional[List[str]] = None
    days_before: int = 30
    days_after: int = 30

# Background task functions
def scrape_trades_task(db: Session, config: dict):
    """Background task to scrape trades"""
    try:
        logger.info("Starting scrape task")
        
        scraper_config = ScraperConfig()
        scraper_config.RECENT_DAYS = config['recent_days']
        scraper_config.MIN_TRADE_SIZE = config['min_trade_size']
        scraper_config.PAGES_TO_SCRAPE = config['pages']
        
        scraper = CapitolTradesScraperSelenium(scraper_config)
        trades = scraper.run()
        
        # Save to database
        saved_count = 0
        for trade_data in trades:
            existing = db.query(Trade).filter(Trade.trade_id == trade_data['trade_id']).first()
            if existing:
                continue
            
            trade = Trade(
                trade_id=trade_data['trade_id'],
                politician=trade_data['politician'],
                party=trade_data['party'],
                trade_issue=trade_data['trade_issue'],
                trade_ticker=trade_data['trade_ticker'],
                transaction_type=trade_data['transaction_type'],
                trade_size_min=trade_data['trade_size'][0] if trade_data['trade_size'] else None,
                trade_size_max=trade_data['trade_size'][1] if trade_data['trade_size'] else None,
                traded_date=trade_data['traded_date'],
                published=trade_data['published'],
                filed_after=trade_data['filed_after'],
                owner=trade_data['owner'],
                price=trade_data['price'],
                trade_link=trade_data['trade_link']
            )
            db.add(trade)
            saved_count += 1
        
        db.commit()
        logger.info(f"Scrape task complete. Saved {saved_count} new trades")
        
    except Exception as e:
        logger.error(f"Error in scrape task: {e}")
        db.rollback()

def analyze_trades_task(db: Session, trade_ids: Optional[List[str]], config: dict):
    """Background task to analyze trades"""
    try:
        logger.info("Starting analysis task")
        
        # Get trades to analyze
        query = db.query(Trade)
        if trade_ids:
            query = query.filter(Trade.trade_id.in_(trade_ids))
        else:
            query = query.filter(Trade.analyzed == False)
        
        trades = query.all()
        
        if not trades:
            logger.info("No trades to analyze")
            return
        
        analyzer = StockPriceAnalyzer(
            days_before=config['days_before'],
            days_after=config['days_after']
        )
        
        for trade in trades:
            try:
                # Convert to dict format expected by analyzer
                trade_data = {
                    'trade_ticker': trade.trade_ticker,
                    'traded_date': trade.traded_date,
                    'politician': trade.politician,
                    'party': trade.party,
                    'transaction_type': trade.transaction_type,
                    'trade_size': [trade.trade_size_min, trade.trade_size_max] if trade.trade_size_min else None,
                    'filed_after': trade.filed_after,
                    'trade_link': trade.trade_link
                }
                
                result = analyzer.analyze_trade(trade_data)
                
                # Save analysis
                analysis = Analysis(
                    trade_id=trade.trade_id,
                    ticker=trade.trade_ticker,
                    politician=trade.politician,
                    party=trade.party,
                    transaction_type=trade.transaction_type,
                    trade_date=trade.traded_date,
                    filed_after=trade.filed_after,
                    metrics=result.get('metrics', {}),
                    chart_data=result.get('chart_data', {}),
                    error=result.get('error')
                )
                db.add(analysis)
                
                trade.analyzed = True
                
            except Exception as e:
                logger.error(f"Error analyzing trade {trade.trade_id}: {e}")
                analysis = Analysis(
                    trade_id=trade.trade_id,
                    ticker=trade.trade_ticker,
                    politician=trade.politician,
                    error=str(e)
                )
                db.add(analysis)
        
        db.commit()
        logger.info(f"Analysis task complete. Analyzed {len(trades)} trades")
        
    except Exception as e:
        logger.error(f"Error in analysis task: {e}")
        db.rollback()

# API Endpoints
@app.get("/")
def root():
    return {"message": "Congressional Trading Analysis API"}

@app.post("/scrape")
def scrape_trades(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start scraping trades in the background"""
    config = {
        'recent_days': request.recent_days,
        'min_trade_size': request.min_trade_size,
        'pages': request.pages
    }
    background_tasks.add_task(scrape_trades_task, db, config)
    return {"message": "Scraping started in background"}

@app.post("/analyze")
def analyze_trades(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start analyzing trades in the background"""
    config = {
        'days_before': request.days_before,
        'days_after': request.days_after
    }
    background_tasks.add_task(analyze_trades_task, db, request.trade_ids, config)
    return {"message": "Analysis started in background"}

@app.get("/trades", response_model=List[TradeResponse])
def get_trades(
    skip: int = 0,
    limit: int = 100,
    politician: Optional[str] = None,
    ticker: Optional[str] = None,
    analyzed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all trades with optional filters"""
    query = db.query(Trade)
    
    if politician:
        query = query.filter(Trade.politician.contains(politician))
    if ticker:
        query = query.filter(Trade.trade_ticker == ticker)
    if analyzed is not None:
        query = query.filter(Trade.analyzed == analyzed)
    
    trades = query.order_by(Trade.scraped_at.desc()).offset(skip).limit(limit).all()
    return trades

@app.get("/trades/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: str, db: Session = Depends(get_db)):
    """Get a specific trade"""
    trade = db.query(Trade).filter(Trade.trade_id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@app.get("/analyses", response_model=List[AnalysisResponse])
def get_analyses(
    skip: int = 0,
    limit: int = 100,
    politician: Optional[str] = None,
    ticker: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all analyses with optional filters"""
    query = db.query(Analysis)
    
    if politician:
        query = query.filter(Analysis.politician.contains(politician))
    if ticker:
        query = query.filter(Analysis.ticker == ticker)
    
    analyses = query.order_by(Analysis.analyzed_at.desc()).offset(skip).limit(limit).all()
    return analyses

@app.get("/analyses/{trade_id}", response_model=AnalysisResponse)
def get_analysis(trade_id: str, db: Session = Depends(get_db)):
    """Get analysis for a specific trade"""
    analysis = db.query(Analysis).filter(Analysis.trade_id == trade_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_trades = db.query(Trade).count()
    analyzed_trades = db.query(Trade).filter(Trade.analyzed == True).count()
    total_analyses = db.query(Analysis).count()
    failed_analyses = db.query(Analysis).filter(Analysis.error.isnot(None)).count()
    
    return {
        "total_trades": total_trades,
        "analyzed_trades": analyzed_trades,
        "unanalyzed_trades": total_trades - analyzed_trades,
        "total_analyses": total_analyses,
        "failed_analyses": failed_analyses,
        "success_rate": round((total_analyses - failed_analyses) / total_analyses * 100, 2) if total_analyses > 0 else 0
    }

@app.delete("/trades/{trade_id}")
def delete_trade(trade_id: str, db: Session = Depends(get_db)):
    """Delete a specific trade"""
    trade = db.query(Trade).filter(Trade.trade_id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    db.delete(trade)
    db.commit()
    return {"message": "Trade deleted"}

@app.delete("/analyses/{trade_id}")
def delete_analysis(trade_id: str, db: Session = Depends(get_db)):
    """Delete analysis for a specific trade"""
    analysis = db.query(Analysis).filter(Analysis.trade_id == trade_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(analysis)
    db.commit()
    return {"message": "Analysis deleted"}