import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Optional


DB_PATH = os.getenv("OPERATING_MIRROR_DB_PATH", "./chroma_db/operating_mirror.db")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_store() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS operating_mirror_graphs (
                graph_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                graph_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS operating_mirror_simulations (
                simulation_id TEXT PRIMARY KEY,
                graph_id TEXT NOT NULL,
                scenario_name TEXT NOT NULL,
                request_json TEXT NOT NULL,
                response_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS operating_mirror_dashboard_snapshots (
                id TEXT PRIMARY KEY,
                simulation_id TEXT,
                dashboard_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS operating_mirror_decisions (
                decision_id TEXT PRIMARY KEY,
                entity_type TEXT,
                entity_id TEXT,
                decision_type TEXT,
                decision_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS operating_mirror_reverse_reviews (
                review_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                decision_id TEXT,
                review_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def upsert_graph(graph: dict[str, Any]) -> None:
    now = _utc_now()
    with _connect() as conn:
        cur = conn.execute(
            "SELECT graph_id, created_at FROM operating_mirror_graphs WHERE graph_id = ?",
            (graph["graph_id"],),
        ).fetchone()
        created_at = cur["created_at"] if cur else now
        conn.execute(
            """
            INSERT OR REPLACE INTO operating_mirror_graphs
            (graph_id, name, version, graph_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                graph["graph_id"],
                graph.get("name", "Willow Operating Mirror"),
                graph.get("version", "1.0.0"),
                json.dumps(graph),
                created_at,
                now,
            ),
        )


def get_graph(graph_id: str) -> Optional[dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT graph_json FROM operating_mirror_graphs WHERE graph_id = ?",
            (graph_id,),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["graph_json"])


def get_any_graph() -> Optional[dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT graph_json FROM operating_mirror_graphs ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["graph_json"])


def save_simulation(simulation_id: str, graph_id: str, scenario_name: str, request: dict[str, Any], response: dict[str, Any]) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO operating_mirror_simulations
            (simulation_id, graph_id, scenario_name, request_json, response_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                simulation_id,
                graph_id,
                scenario_name,
                json.dumps(request),
                json.dumps(response),
                _utc_now(),
            ),
        )


def get_simulation(simulation_id: str) -> Optional[dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT response_json FROM operating_mirror_simulations WHERE simulation_id = ?",
            (simulation_id,),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["response_json"])


def save_dashboard(snapshot_id: str, simulation_id: Optional[str], dashboard: dict[str, Any]) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO operating_mirror_dashboard_snapshots
            (id, simulation_id, dashboard_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                snapshot_id,
                simulation_id,
                json.dumps(dashboard),
                _utc_now(),
            ),
        )


def get_latest_dashboard() -> Optional[dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT dashboard_json FROM operating_mirror_dashboard_snapshots ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["dashboard_json"])


def upsert_decision(decision: dict[str, Any]) -> None:
    now = _utc_now()
    with _connect() as conn:
        existing = conn.execute(
            "SELECT created_at FROM operating_mirror_decisions WHERE decision_id = ?",
            (decision["decision_id"],),
        ).fetchone()
        created_at = existing["created_at"] if existing else now
        conn.execute(
            """
            INSERT OR REPLACE INTO operating_mirror_decisions
            (decision_id, entity_type, entity_id, decision_type, decision_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision["decision_id"],
                decision.get("entity_type"),
                decision.get("entity_id"),
                decision.get("decision_type"),
                json.dumps(decision),
                created_at,
                now,
            ),
        )


def get_decision(decision_id: str) -> Optional[dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT decision_json FROM operating_mirror_decisions WHERE decision_id = ?",
            (decision_id,),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["decision_json"])


def save_reverse_review(review_id: str, entity_type: str, entity_id: str, decision_id: Optional[str], review: dict[str, Any]) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO operating_mirror_reverse_reviews
            (review_id, entity_type, entity_id, decision_id, review_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                review_id,
                entity_type,
                entity_id,
                decision_id,
                json.dumps(review),
                _utc_now(),
            ),
        )
