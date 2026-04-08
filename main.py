"""
Tech Events Hub — Multi-Agent System
Primary entry point. Runs the FastAPI server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from orchestrator import router as orchestrator_router
from events import router as events_router
from orders import router as orders_router
from analytics import router as analytics_router
from fastapi.responses import FileResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print("❌ DB init failed:", e)
    yield

app = FastAPI(
    title="Tech Events Hub — Multi-Agent System",
    description="Multi-agent AI system for event management via Ticket Tailor MCP",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orchestrator_router, prefix="/orchestrator", tags=["Orchestrator"])
app.include_router(events_router,       prefix="/events",       tags=["Event Agent"])
app.include_router(orders_router,       prefix="/orders",       tags=["Orders Agent"])
app.include_router(analytics_router,    prefix="/analytics",    tags=["Analytics Agent"])

@app.get("/")
async def root():
    return {
        "system": "Tech Events Hub — Multi-Agent System",
        "agents": ["Orchestrator", "Event Agent", "Ticket Agent", "Orders Agent", "Analytics Agent"],
        "mcp": "Ticket Tailor",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
from fastapi.responses import FileResponse

@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")