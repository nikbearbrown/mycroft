from fastapi import APIRouter, HTTPException
from app.models import FeedQuery, ChatResponse
from app.crud import FeedCRUD
from app.rag import get_rag_engine

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def ask_question(query: FeedQuery):
    """Ask a question about selected regulatory feeds"""
    
    # Validate feed IDs exist
    feeds = FeedCRUD.get_feeds_by_ids(query.feed_ids)
    
    if not feeds:
        raise HTTPException(
            status_code=404,
            detail="None of the provided feed IDs were found"
        )
    
    if len(feeds) != len(query.feed_ids):
        found_ids = {feed.id for feed in feeds}
        missing = set(query.feed_ids) - found_ids
        raise HTTPException(
            status_code=404,
            detail=f"Some feed IDs not found: {list(missing)}"
        )
    
    # Get RAG engine and build context
    rag = get_rag_engine()
    rag.build_vectorstore(feeds)
    
    # Query
    try:
        result = await rag.query(query.question)  # Now async
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            context_count=len(feeds)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )