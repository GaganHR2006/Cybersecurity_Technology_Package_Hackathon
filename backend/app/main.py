from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import alerts, incidents, responses, metrics

app = FastAPI(
    title="CyberWatch Intelligence Platform",
    description="Open-Source Cybersecurity Monitoring, Correlation & Incident Response API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(alerts.router, prefix="/api/v1")
app.include_router(incidents.router, prefix="/api/v1")
app.include_router(responses.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "CyberWatch Intelligence Platform"}
