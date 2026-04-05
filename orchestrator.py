"""
Orchestrator Agent
Primary coordinator. Receives user requests, plans workflows,
delegates to sub-agents, and synthesizes final responses.
Uses Claude claude-sonnet-4-20250514 with Ticket Tailor MCP.
"""
import os
import json
import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from database import log_agent_action, save_workflow
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MCP_SERVER_URL = "https://mcp.tickettailor.ai/mcp"

SYSTEM_PROMPT = """You are the Orchestrator Agent for "Tech Events Hub" — a multi-agent event management system.

You coordinate a team of specialized sub-agents:
- Event Agent: creates/manages Ticket Tailor event series and occurrences
- Ticket Agent: manages ticket types, pricing, bundles, vouchers
- Orders Agent: tracks orders, issued tickets, check-ins
- Analytics Agent: generates revenue reports and insights

You have direct access to the Ticket Tailor MCP tools. When the user asks you to:
- Create/manage events → use event_management, event_series tools
- Handle tickets/pricing → use ticket_type, bundle, voucher tools
- Track orders → use orders_get, issued_tickets tools
- Check-in attendees → use check_in_create
- Get reports → use overview_get, orders_get with filters

Always:
1. Understand the user's goal
2. Break it into steps if needed
3. Use the right MCP tools
4. Summarize what you did clearly

Be concise, professional, and action-oriented."""


class OrchestratorRequest(BaseModel):
    user_input: str
    workflow_context: dict = {}


class OrchestratorResponse(BaseModel):
    result: str
    steps_taken: list
    agent: str = "orchestrator"


@router.post("/run", response_model=OrchestratorResponse)
async def run_orchestrator(req: OrchestratorRequest):
    """
    Main orchestrator endpoint. Receives user request and coordinates agents.
    """
    steps = []

    # Step 1: Log the incoming request
    await log_agent_action("orchestrator", "receive_request", {"input": req.user_input})
    steps.append({"step": 1, "action": "request_received", "agent": "orchestrator"})

    # Step 2: Call Claude API with MCP tools
    result = await _call_claude_with_mcp(req.user_input, steps)

    # Step 3: Save workflow to DB
    await save_workflow(
        workflow="orchestrator_run",
        user_input=req.user_input,
        steps=steps,
        final_result={"result": result}
    )
    steps.append({"step": len(steps) + 1, "action": "workflow_saved", "agent": "orchestrator"})

    return OrchestratorResponse(result=result, steps_taken=steps)


async def _call_claude_with_mcp(user_input: str, steps: list) -> str:
    """
    Calls Claude API with Ticket Tailor MCP server attached.
    Claude will autonomously use MCP tools to fulfill the request.
    """
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_input}],
        "mcp_servers": [
            {
                "type": "url",
                "url": MCP_SERVER_URL,
                "name": "ticket-tailor"
            }
        ]
    }

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "mcp-client-2025-04-04",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

    # Extract text from response
    full_text = ""
    tool_uses = []
    for block in data.get("content", []):
        if block.get("type") == "text":
            full_text += block["text"]
        elif block.get("type") == "tool_use":
            tool_uses.append(block.get("name", "unknown_tool"))

    # Log tool uses as steps
    for tool in tool_uses:
        steps.append({"action": f"mcp_tool: {tool}", "agent": "orchestrator"})
        await log_agent_action("orchestrator", f"used_tool: {tool}", {"tool": tool})

    return full_text or "Orchestrator completed the task."


@router.get("/logs")
async def get_logs():
    """Returns recent agent action logs from DB."""
    from database import get_recent_logs
    return {"logs": await get_recent_logs(20)}


@router.get("/history")
async def get_history():
    """Returns workflow run history from DB."""
    from database import get_workflow_history
    return {"history": await get_workflow_history(10)}
