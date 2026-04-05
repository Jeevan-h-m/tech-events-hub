"""Analytics Agent — generates reports and insights"""
from fastapi import APIRouter
from database import log_agent_action, get_recent_logs, get_workflow_history
import mcp_client

router = APIRouter()

@router.get("/overview")
async def get_overview():
    """Full box office overview from Ticket Tailor."""
    await log_agent_action("analytics_agent", "get_overview")
    data = await mcp_client.get_overview()
    return {"agent": "analytics_agent", "overview": data}

@router.get("/report")
async def get_report():
    """Combines Ticket Tailor data + local DB for a full report."""
    await log_agent_action("analytics_agent", "get_report")
    overview = await mcp_client.get_overview()
    orders = await mcp_client.list_orders(limit=50)
    logs = await get_recent_logs(10)
    history = await get_workflow_history(5)
    return {
        "agent": "analytics_agent",
        "report": {
            "box_office": overview,
            "recent_orders": orders,
            "agent_activity": logs,
            "workflow_history": history
        }
    }

@router.get("/stores")
async def get_stores():
    await log_agent_action("analytics_agent", "get_stores")
    data = await mcp_client.get_store_list()
    return {"agent": "analytics_agent", "stores": data}
