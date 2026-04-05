"""Orders Agent — tracks orders, issued tickets, check-ins"""
from fastapi import APIRouter
from typing import Optional
from database import log_agent_action, cache_order
import mcp_client

router = APIRouter()

@router.get("/list")
async def list_orders(event_id: Optional[str] = None, status: Optional[str] = None):
    await log_agent_action("orders_agent", "list_orders", {"event_id": event_id, "status": status})
    data = await mcp_client.list_orders(event_id=event_id, status=status)
    return {"agent": "orders_agent", "orders": data}

@router.get("/{order_id}")
async def get_order(order_id: str):
    await log_agent_action("orders_agent", "get_order", {"order_id": order_id})
    data = await mcp_client.get_order(order_id)
    return {"agent": "orders_agent", "order": data}

@router.get("/tickets/issued")
async def list_issued_tickets(event_id: Optional[str] = None):
    await log_agent_action("orders_agent", "list_issued_tickets", {"event_id": event_id})
    data = await mcp_client.list_issued_tickets(event_id=event_id)
    return {"agent": "orders_agent", "issued_tickets": data}

@router.post("/check-in/{issued_ticket_id}")
async def check_in(issued_ticket_id: str):
    await log_agent_action("orders_agent", "check_in", {"ticket_id": issued_ticket_id})
    data = await mcp_client.create_check_in(issued_ticket_id)
    return {"agent": "orders_agent", "check_in": data}
