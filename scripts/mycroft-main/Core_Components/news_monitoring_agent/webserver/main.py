from typing import Dict, List, Optional
from fastapi import FastAPI, Depends, Request, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .utils import fetch_normalize_data, parse_article, finbert_pipeline
import asyncio
import logging
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)
app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    response_time = time.perf_counter() - start_time
    logger.info(
        f"{request.method} {request.url.path} {response.status_code} {response_time:.3f}s"
    )
    return response


class ModelResources:
    def __init__(self):
        self.finbert = finbert_pipeline()


resources = None


@app.on_event("startup")
async def load_model():
    global resources
    resources = ModelResources()


def get_finbert():
    return resources.finbert


# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://n8n:*",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get("/")
async def root():
    return Response("Hello World", status_code=200)


@app.get("/health")
async def health():
    return Response(status_code=200)


class FetchRequest(BaseModel):
    feed_url: str
    lib: str
    search_terms: Optional[List[str]] = None
    last_updated: Optional[float] = None


@app.post("/fetch")
async def fetch(request: FetchRequest):
    logger.info(f"Fetch request received: {request}")
    return await asyncio.to_thread(
        fetch_normalize_data,
        request.feed_url,
        request.lib,
        request.last_updated,
        request.search_terms,
    )


@app.post("/parse")
async def parse(article: Dict):
    return await asyncio.to_thread(parse_article, article)


@app.post("/finbert")
async def apply_finbert(article: str, finbert=Depends(get_finbert)):
    try:
        return await asyncio.to_thread(finbert, article, truncation="only_first")
    except Exception as e:
        print(e)
        return {}
