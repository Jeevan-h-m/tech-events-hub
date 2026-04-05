"""
Tech Events Hub — Multi-Agent System
Primary entry point. Runs the FastAPI server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import orchestrator, events, tickets, orders, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("✅ Database initialized")
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

app.include_router(orchestrator.router, prefix="/orchestrator", tags=["Orchestrator"])
app.include_router(events.router,       prefix="/events",       tags=["Event Agent"])
app.include_router(tickets.router,      prefix="/tickets",      tags=["Ticket Agent"])
app.include_router(orders.router,       prefix="/orders",       tags=["Orders Agent"])
app.include_router(analytics.router,    prefix="/analytics",    tags=["Analytics Agent"])

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
