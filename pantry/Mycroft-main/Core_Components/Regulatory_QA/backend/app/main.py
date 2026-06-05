from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import feeds, chat
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Mycroft Regulatory Intelligence API",
    description="QA system for financial regulatory feeds",
    version="1.0.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite/React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(feeds.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {
        "message": "Mycroft Regulatory Intelligence API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )