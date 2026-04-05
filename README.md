# 🎟️ Tech Events Hub — Multi-Agent AI System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Claude AI](https://img.shields.io/badge/Claude-3.5_Sonnet-D97706?style=for-the-badge&logo=anthropic&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A production-grade multi-agent AI system that manages events, tickets, orders, and analytics using Claude AI as the orchestrator and Ticket Tailor MCP for real event data.**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API Docs](#-api-endpoints) • [Docker](#-docker-deployment)

</div>

---

## ✨ Features

- 🤖 **Multi-Agent Coordination** — Orchestrator delegates tasks to 4 specialized sub-agents
- 🎟️ **Ticket Tailor MCP** — 65+ real tools for event, ticket, order and check-in management
- 🗄️ **SQLite Database** — Persists agent logs, workflow history, and event cache
- 🔄 **Multi-Step Workflows** — Natural language input → automatic multi-tool execution
- 🚀 **REST API** — FastAPI with auto-generated Swagger docs at `/docs`
- 🐳 **Docker Ready** — Single command deployment
- 🔐 **Secure** — API keys via environment variables, never hardcoded

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      USER REQUEST                        │
│        "Create a tech meetup with 3 ticket tiers"        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATOR AGENT  (Primary)               │
│              Claude claude-sonnet-4-20250514 + MCP                │
│   • Parses user intent                                   │
│   • Plans multi-step workflow                            │
│   • Delegates to sub-agents                              │
│   • Synthesizes final response                           │
└──────┬───────────────┬───────────────┬──────────────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐
│  EVENT   │   │  TICKET  │   │  ORDERS  │   │  ANALYTICS   │
│  AGENT   │   │  AGENT   │   │  AGENT   │   │    AGENT     │
│ • Create │   │ • Types  │   │ • Orders │   │ • Revenue    │
│ • Series │   │ • Bundles│   │ • Checkin│   │ • Reports    │
│ • Events │   │ • Voucher│   │ • Tickets│   │ • Insights   │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └──────┬───────┘
     └───────────────┴──────────────┴────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  TICKET TAILOR MCP                       │
│   Box Office: Tech Events Hub  |  Currency: USD          │
│   Store ID: st_78746           |  65+ Live API Tools     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   SQLite DATABASE                        │
│       agent_logs • workflow_runs • events_cache          │
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 Agent Responsibilities

| Agent | Role | Key MCP Tools |
|-------|------|---------------|
| **Orchestrator** | Primary coordinator — routes & synthesizes | All tools via Claude AI |
| **Event Agent** | Create and manage events and series | `events_get`, `event_series_*`, `event_management` |
| **Ticket Agent** | Pricing, bundles, vouchers, holds | `ticket_type_*`, `bundle_*`, `voucher_*`, `holds_*` |
| **Orders Agent** | Track orders, issued tickets, check-ins | `orders_get`, `issued_tickets_*`, `check_in_*` |
| **Analytics Agent** | Revenue reports and insights | `overview_get`, `store_get`, SQLite queries |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- [Anthropic API Key](https://console.anthropic.com/)
- [Ticket Tailor API Key](https://www.tickettailor.com/settings/api)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/tech-events-hub.git
cd tech-events-hub
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
TICKET_TAILOR_API_KEY=sk_xxxxxxxxxxxxxxxx
```

### 4. Run the server

```bash
uvicorn main:app --reload --port 8000
```

### 5. Open API docs

```
http://localhost:8000/docs
```

---

## 🐳 Docker Deployment

### Run with Docker

```bash
# Build the image
docker build -t tech-events-hub .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key_here \
  -e TICKET_TAILOR_API_KEY=your_key_here \
  --name tech-events-hub \
  tech-events-hub
```

### Run with Docker Compose

```bash
# Copy and fill in your keys
cp .env.example .env

# Start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

---

## 📡 API Endpoints

### Orchestrator — Natural Language Workflows

```http
POST /orchestrator/run
Content-Type: application/json

{
  "user_input": "Create a tech conference for May 2026 with Early Bird and VIP tickets"
}
```

**Response:**

```json
{
  "result": "Created event 'Tech Conference May 2026' with 2 ticket tiers...",
  "steps_taken": [
    {"step": 1, "action": "request_received", "agent": "orchestrator"},
    {"step": 2, "action": "mcp_tool: event_management", "agent": "orchestrator"},
    {"step": 3, "action": "mcp_tool: ticket_type_update", "agent": "orchestrator"}
  ],
  "agent": "orchestrator"
}
```

### Full Endpoint Reference

| Method | Endpoint | Agent | Description |
|--------|----------|-------|-------------|
| `POST` | `/orchestrator/run` | Orchestrator | Run natural language workflow |
| `GET` | `/orchestrator/logs` | Orchestrator | View agent action logs |
| `GET` | `/orchestrator/history` | Orchestrator | View workflow run history |
| `GET` | `/events/list` | Event Agent | List all events |
| `GET` | `/events/series` | Event Agent | List event series |
| `GET` | `/events/series/{id}` | Event Agent | Get specific event series |
| `GET` | `/tickets/vouchers` | Ticket Agent | List all vouchers |
| `GET` | `/orders/list` | Orders Agent | List all orders |
| `GET` | `/orders/{id}` | Orders Agent | Get order by ID |
| `GET` | `/orders/tickets/issued` | Orders Agent | List issued tickets |
| `POST` | `/orders/check-in/{id}` | Orders Agent | Check in a ticket |
| `GET` | `/analytics/overview` | Analytics Agent | Box office overview |
| `GET` | `/analytics/report` | Analytics Agent | Full combined report |
| `GET` | `/analytics/stores` | Analytics Agent | List stores |

---

## 💬 Example Workflows

### Create an event with tickets

```bash
curl -X POST http://localhost:8000/orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Create a tech meetup for next month with Free and VIP ticket types"}'
```

### Get revenue overview

```bash
curl -X POST http://localhost:8000/orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Show me revenue and ticket stats for this month"}'
```

### Create a discount voucher

```bash
curl -X POST http://localhost:8000/orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Create a 20% discount voucher code EARLYBIRD for my events"}'
```

### Check in an attendee

```bash
curl -X POST http://localhost:8000/orders/check-in/it_xxxxxxxx
```

---

## 🗂️ Project Structure

```
tech-events-hub/
├── main.py                   # FastAPI app entry point
├── database.py               # SQLite setup, logging, caching
├── mcp_client.py             # Ticket Tailor API wrapper
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Multi-container orchestration
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI/CD pipeline
└── routers/
    ├── __init__.py
    ├── orchestrator.py       # Primary coordinator agent
    ├── events.py             # Event Agent
    ├── tickets.py            # Ticket Agent
    ├── orders.py             # Orders Agent
    └── analytics.py          # Analytics Agent
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI 0.115 |
| AI Orchestrator | Claude claude-sonnet-4-20250514 (Anthropic) |
| MCP Integration | Ticket Tailor MCP (65+ tools) |
| Database | SQLite via aiosqlite |
| HTTP Client | httpx (async) |
| Config | python-dotenv |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## 🔐 Security

- API keys are loaded from environment variables — **never hardcoded**
- `.env` is excluded from git via `.gitignore`
- Only `.env.example` (with placeholder values) is committed to the repo
- Docker secrets can be passed via `-e` flags or Docker secrets manager

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with Claude AI + Ticket Tailor MCP | Tech Events Hub
</div>
