"""Event Agent — manages events via Ticket Tailor MCP"""
from fastapi import APIRouter
from database import log_agent_action
import mcp_client

router = APIRouter()

@router.get("/list")
async def list_events():
    """List all events from Ticket Tailor."""
    await log_agent_action("event_agent", "list_events")
    data = await mcp_client.list_events()
    return {"agent": "event_agent", "events": data}

@router.get("/series")
async def list_event_series():
    """List all event series from Ticket Tailor."""
    await log_agent_action("event_agent", "list_event_series")
    data = await mcp_client.list_event_series()
    return {"agent": "event_agent", "event_series": data}

@router.get("/series/{series_id}")
async def get_event_series(series_id: str):
    """Get a specific event series."""
    await log_agent_action("event_agent", "get_event_series", {"series_id": series_id})
    data = await mcp_client.get_event_series(series_id)
    return {"agent": "event_agent", "series": data}
