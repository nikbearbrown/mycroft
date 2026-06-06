import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.config import get_settings

settings = get_settings()

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = psycopg2.connect(settings.database_url)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_cursor(conn):
    """Get a cursor that returns dict-like rows"""
    return conn.cursor(cursor_factory=RealDictCursor)