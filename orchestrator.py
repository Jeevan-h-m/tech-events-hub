"""
Orchestrator Agent
Primary coordinator. Receives user requests, plans workflows,
delegates to sub-agents, and synthesizes final responses.
Uses Claude claude-sonnet-4-20250514 via Anthropic API.
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
TICKET_TAILOR_API_KEY = os.getenv("TICKET_TAILOR_API_KEY", "")

SYSTEM_PROMPT = """You are the Orchestrator Agent for "Tech Events Hub" — a multi-agent AI event management system built on Ticket Tailor.

You coordinate 4 specialized sub-agents:
- Event Agent: manages Ticket Tailor event series and occurrences
- Ticket Agent: manages ticket types, pricing, bundles, vouchers
- Orders Agent: tracks orders, issued tickets, and check-ins
- Analytics Agent: generates revenue reports and insights

The user's Ticket Tailor box office is called "Tech Events Hub" (store ID: st_78746, currency: USD).

When the user asks you something, respond in this exact JSON format:
{
  "agent": "event_agent | ticket_agent | orders_agent | analytics_agent | orchestrator",
  "action": "short description of what you will do",
  "response": "your full helpful response to the user",
  "next_steps": ["optional list of suggested follow-up actions"]
}

Be concise, professional, and action-oriented. Always refer to real Ticket Tailor capabilities."""


class OrchestratorRequest(BaseModel):
    user_input: str
    workflow_context: dict = {}


class OrchestratorResponse(BaseModel):
    result: str
    steps_taken: list
    agent: str = "orchestrator"
    delegated_to: str = ""
    next_steps: list = []


@router.post("/run", response_model=OrchestratorResponse)
async def run_orchestrator(req: OrchestratorRequest):
    """
    Main orchestrator endpoint. Receives user request and coordinates agents.
    """
    steps = []

    # Step 1: Log the incoming request
    await log_agent_action("orchestrator", "receive_request", {"input": req.user_input})
    steps.append({"step": 1, "action": "request_received", "agent": "orchestrator"})

    # Step 2: Call Claude API to plan and respond
    claude_result = await _call_claude(req.user_input)
    steps.append({"step": 2, "action": "claude_planning_complete", "agent": "orchestrator"})

    # Step 3: Parse Claude's structured response
    delegated_to = claude_result.get("agent", "orchestrator")
    action = claude_result.get("action", "")
    response_text = claude_result.get("response", "Task completed.")
    next_steps = claude_result.get("next_steps", [])

    steps.append({"step": 3, "action": f"delegated_to: {delegated_to} — {action}", "agent": "orchestrator"})

    # Step 4: Log delegation
    await log_agent_action("orchestrator", f"delegated_to_{delegated_to}", {"action": action})

    # Step 5: Save workflow to DB
    await save_workflow(
        workflow="orchestrator_run",
        user_input=req.user_input,
        steps=steps,
        final_result={"result": response_text, "delegated_to": delegated_to}
    )
    steps.append({"step": 4, "action": "workflow_saved_to_db", "agent": "orchestrator"})

    return OrchestratorResponse(
        result=response_text,
        steps_taken=steps,
        agent="orchestrator",
        delegated_to=delegated_to,
        next_steps=next_steps
    )


async def _call_claude(user_input: str) -> dict:
    """
    Calls Claude claude-sonnet-4-20250514 via Anthropic API.
    Returns structured JSON response for agent routing.
    """
    if not ANTHROPIC_API_KEY:
        return {
            "agent": "orchestrator",
            "action": "error",
            "response": "ANTHROPIC_API_KEY is not set. Please add it to Railway environment variables.",
            "next_steps": ["Add ANTHROPIC_API_KEY in Railway → Variables tab"]
        }

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_input}]
    }

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

        # Extract text from response
        raw_text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                raw_text += block["text"]

        # Try to parse as JSON
        try:
            # Strip markdown code fences if present
            clean = raw_text.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except json.JSONDecodeError:
            # If not JSON, wrap the raw text
            return {
                "agent": "orchestrator",
                "action": "direct_response",
                "response": raw_text,
                "next_steps": []
            }

    except httpx.HTTPStatusError as e:
        error_body = e.response.text if e.response else str(e)
        await log_agent_action("orchestrator", "claude_api_error", {"error": error_body}, status="error")
        return {
            "agent": "orchestrator",
            "action": "api_error",
            "response": f"Claude API error: {e.response.status_code}. Check your ANTHROPIC_API_KEY in Railway variables.",
            "next_steps": ["Verify ANTHROPIC_API_KEY is correctly set in Railway → Variables"]
        }
    except Exception as e:
        await log_agent_action("orchestrator", "unexpected_error", {"error": str(e)}, status="error")
        return {
            "agent": "orchestrator",
            "action": "unexpected_error",
            "response": f"Unexpected error: {str(e)}",
            "next_steps": []
        }


@router.get("/logs")
async def get_logs():
    """Returns recent agent action logs from DB."""
    from database import get_recent_logs
    logs = await get_recent_logs(20)
    return {"logs": logs}


@router.get("/history")
async def get_history():
    """Returns workflow run history from DB."""
    from database import get_workflow_history
    history = await get_workflow_history(10)
    return {"history": history}


@router.get("/status")
async def get_status():
    """Returns system status and environment check."""
    return {
        "system": "Tech Events Hub Multi-Agent System",
        "anthropic_key_set": bool(ANTHROPIC_API_KEY),
        "ticket_tailor_key_set": bool(TICKET_TAILOR_API_KEY),
        "agents": ["orchestrator", "event_agent", "ticket_agent", "orders_agent", "analytics_agent"],
        "mcp": "Ticket Tailor (st_78746)",
        "status": "running"
    }
