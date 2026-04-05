"""
Ticket Tailor MCP Client
Wraps all Ticket Tailor API calls used by the agents.
Set TICKET_TAILOR_API_KEY in your .env file.
"""
import os
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.tickettailor.com/v1"

def _headers():
    api_key = os.getenv("TICKET_TAILOR_API_KEY", "")
    import base64
    encoded = base64.b64encode(f"{api_key}:".encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


async def get_overview() -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/dashboard", headers=_headers())
        r.raise_for_status()
        return r.json()


async def list_event_series(limit: int = 10) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/event_series", headers=_headers(), params={"limit": limit})
        r.raise_for_status()
        return r.json()


async def get_event_series(series_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/event_series/{series_id}", headers=_headers())
        r.raise_for_status()
        return r.json()


async def list_events(limit: int = 20) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/events", headers=_headers(), params={"limit": limit})
        r.raise_for_status()
        return r.json()


async def list_orders(
    event_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20
) -> dict:
    params = {"limit": limit}
    if event_id:
        params["event_id"] = event_id
    if status:
        params["status"] = status
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/orders", headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()


async def get_order(order_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/orders/{order_id}", headers=_headers())
        r.raise_for_status()
        return r.json()


async def list_issued_tickets(event_id: Optional[str] = None) -> dict:
    params = {}
    if event_id:
        params["event_id"] = event_id
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/issued_tickets", headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()


async def create_check_in(issued_ticket_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/issued_tickets/{issued_ticket_id}/check_ins",
            headers=_headers()
        )
        r.raise_for_status()
        return r.json()


async def list_vouchers() -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/vouchers", headers=_headers())
        r.raise_for_status()
        return r.json()


async def get_store_list() -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/stores", headers=_headers())
        r.raise_for_status()
        return r.json()
