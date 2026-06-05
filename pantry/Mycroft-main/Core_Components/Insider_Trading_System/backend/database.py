from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./congressional_trades.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True)
    politician = Column(String, index=True)
    party = Column(String)
    trade_issue = Column(String)
    trade_ticker = Column(String, index=True)
    transaction_type = Column(String)
    trade_size_min = Column(Integer)
    trade_size_max = Column(Integer)
    traded_date = Column(String)
    published = Column(String)
    filed_after = Column(Integer)
    owner = Column(String)
    price = Column(String)
    trade_link = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    analyzed = Column(Boolean, default=False)

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, index=True)
    ticker = Column(String)
    politician = Column(String)
    party = Column(String)
    transaction_type = Column(String)
    trade_date = Column(String)
    filed_after = Column(Integer)
    
    # Metrics stored as JSON
    metrics = Column(JSON)
    
    # Chart data stored as JSON
    chart_data = Column(JSON)  # Contains: dates, prices, volumes, trade_date_index
    
    # Analysis metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    error = Column(String, nullable=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)