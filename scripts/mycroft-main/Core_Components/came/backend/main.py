from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.session import init_db
from routers import events, strategy, capital, metrics

app = FastAPI(title="CAME — Capital Allocation Memory Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(strategy.router)
app.include_router(capital.router)
app.include_router(metrics.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
