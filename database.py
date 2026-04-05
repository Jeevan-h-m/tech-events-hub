"""
Database layer — SQLite via aiosqlite
Stores agent logs, workflow history, and cached event data.
"""
import aiosqlite
import json
from datetime import datetime

DB_PATH = "events_hub.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            agent       TEXT NOT NULL,
            action      TEXT NOT NULL,
            payload     TEXT,
            result      TEXT,
            status      TEXT DEFAULT 'ok',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS workflow_runs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow    TEXT NOT NULL,
            user_input  TEXT NOT NULL,
            steps       TEXT,
            final_result TEXT,
            status      TEXT DEFAULT 'pending',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS events_cache (
            event_id    TEXT PRIMARY KEY,
            name        TEXT,
            data        TEXT,
            synced_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS orders_cache (
            order_id    TEXT PRIMARY KEY,
            event_id    TEXT,
            customer    TEXT,
            data        TEXT,
            synced_at   TEXT DEFAULT (datetime('now'))
        );
        """)
        await db.commit()


async def log_agent_action(agent: str, action: str, payload: dict = None, result: dict = None, status: str = "ok"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO agent_logs (agent, action, payload, result, status) VALUES (?,?,?,?,?)",
            (agent, action, json.dumps(payload), json.dumps(result), status)
        )
        await db.commit()


async def save_workflow(workflow: str, user_input: str, steps: list, final_result: dict, status: str = "completed"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO workflow_runs (workflow, user_input, steps, final_result, status) VALUES (?,?,?,?,?)",
            (workflow, user_input, json.dumps(steps), json.dumps(final_result), status)
        )
        await db.commit()


async def get_recent_logs(limit: int = 20) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_workflow_history(limit: int = 10) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM workflow_runs ORDER BY created_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def cache_event(event_id: str, name: str, data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO events_cache (event_id, name, data, synced_at) VALUES (?,?,?,?)",
            (event_id, name, json.dumps(data), datetime.utcnow().isoformat())
        )
        await db.commit()


async def cache_order(order_id: str, event_id: str, customer: str, data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO orders_cache (order_id, event_id, customer, data, synced_at) VALUES (?,?,?,?,?)",
            (order_id, event_id, customer, json.dumps(data), datetime.utcnow().isoformat())
        )
        await db.commit()
