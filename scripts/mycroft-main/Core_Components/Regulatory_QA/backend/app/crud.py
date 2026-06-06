from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database import get_db, get_cursor
from app.models import Feed

class FeedCRUD:
    
    @staticmethod
    def list_feeds(
        source_feed: Optional[str] = None,
        min_urgency: Optional[int] = None,
        max_urgency: Optional[int] = None,
        impact_level: Optional[str] = None,
        categories: Optional[List[str]] = None,
        is_enforcement: Optional[bool] = None,
        has_deadline: Optional[bool] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Query feeds with flexible filtering"""
        with get_db() as conn:
            cursor = get_cursor(conn)
            
            conditions = []
            params = []
            
            if source_feed:
                conditions.append("source_feed = %s")
                params.append(source_feed)
            
            if min_urgency is not None:
                conditions.append("urgency_score >= %s")
                params.append(min_urgency)
            
            if max_urgency is not None:
                conditions.append("urgency_score <= %s")
                params.append(max_urgency)
            
            if impact_level:
                conditions.append("impact_level = %s")
                params.append(impact_level)
            
            if categories:
                conditions.append("categories ?| %s")
                params.append(categories)
            
            if is_enforcement is not None:
                conditions.append("is_enforcement = %s")
                params.append(is_enforcement)
            
            if has_deadline is not None:
                conditions.append("has_deadline = %s")
                params.append(has_deadline)
            
            if date_from:
                conditions.append("published >= %s")
                params.append(date_from)
            
            if date_to:
                conditions.append("published <= %s")
                params.append(date_to)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            # Count total
            count_query = f"SELECT COUNT(*) FROM regulatory_feeds {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['count']
            
            # Get feeds - select only columns that exist
            query = f"""
                SELECT 
                    id, source_feed, source, title, link, published, content,
                    urgency_score, impact_level, keyword_matches, categories,
                    word_count, has_deadline, is_enforcement, 
                    email_sent, scraped_at, created_at
                FROM regulatory_feeds
                {where_clause}
                ORDER BY created_at DESC, urgency_score DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, params + [limit, offset])
            feeds = cursor.fetchall()
            
            return {
                "total": total,
                "feeds": [Feed(**feed) for feed in feeds],
                "filters_applied": {
                    "source_feed": source_feed,
                    "min_urgency": min_urgency,
                    "max_urgency": max_urgency,
                    "impact_level": impact_level,
                    "categories": categories,
                    "is_enforcement": is_enforcement,
                    "has_deadline": has_deadline,
                    "date_from": date_from,
                    "date_to": date_to
                }
            }
    
    @staticmethod
    def get_feed_by_id(feed_id: int) -> Optional[Feed]:
        """Get single feed by ID"""
        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute(
                """
                SELECT 
                    id, source_feed, source, title, link, published, content,
                    urgency_score, impact_level, keyword_matches, categories,
                    word_count, has_deadline, is_enforcement, 
                    email_sent, scraped_at, created_at
                FROM regulatory_feeds 
                WHERE id = %s
                """, 
                (feed_id,)
            )
            feed = cursor.fetchone()
            return Feed(**feed) if feed else None
    
    @staticmethod
    def get_feeds_by_ids(feed_ids: List[int]) -> List[Feed]:
        """Get multiple feeds by IDs - for RAG context"""
        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute(
                """
                SELECT 
                    id, source_feed, source, title, link, published, content,
                    urgency_score, impact_level, keyword_matches, categories,
                    word_count, has_deadline, is_enforcement, 
                    email_sent, scraped_at, created_at
                FROM regulatory_feeds 
                WHERE id = ANY(%s)
                """,
                (feed_ids,)
            )
            feeds = cursor.fetchall()
            return [Feed(**feed) for feed in feeds]
    
    @staticmethod
    def get_recent_feeds(days: int = 7, limit: int = 20) -> List[Feed]:
        """Get recent feeds for dashboard"""
        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute(
                """
                SELECT 
                    id, source_feed, source, title, link, published, content,
                    urgency_score, impact_level, keyword_matches, categories,
                    word_count, has_deadline, is_enforcement, 
                    email_sent, scraped_at, created_at
                FROM regulatory_feeds
                WHERE created_at >= NOW() - INTERVAL '%s days'
                ORDER BY urgency_score DESC, created_at DESC
                LIMIT %s
                """,
                (days, limit)
            )
            feeds = cursor.fetchall()
            return [Feed(**feed) for feed in feeds]
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get dashboard statistics"""
        with get_db() as conn:
            cursor = get_cursor(conn)
            
            # Total counts
            cursor.execute("SELECT COUNT(*) as total FROM regulatory_feeds")
            total = cursor.fetchone()['total']
            
            # By urgency
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE urgency_score >= 8) as critical,
                    COUNT(*) FILTER (WHERE urgency_score BETWEEN 6 AND 7) as high,
                    COUNT(*) FILTER (WHERE urgency_score BETWEEN 4 AND 5) as medium,
                    COUNT(*) FILTER (WHERE urgency_score <= 3) as low
                FROM regulatory_feeds
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """)
            urgency_stats = cursor.fetchone()
            
            # By source
            cursor.execute("""
                SELECT source_feed, COUNT(*) as count
                FROM regulatory_feeds
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY source_feed
                ORDER BY count DESC
            """)
            source_stats = cursor.fetchall()
            
            # Recent activity
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM regulatory_feeds
                WHERE created_at >= NOW() - INTERVAL '14 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            activity = cursor.fetchall()
            
            return {
                "total_feeds": total,
                "urgency_distribution": dict(urgency_stats),
                "source_distribution": {row['source_feed']: row['count'] for row in source_stats},
                "recent_activity": [{"date": row['date'].isoformat(), "count": row['count']} for row in activity]
            }