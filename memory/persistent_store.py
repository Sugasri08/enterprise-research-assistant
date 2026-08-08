"""
Module 9 — Memory (persistent + long-term).
Stores past client conversations and a per-client profile (preferred
report style, frequently researched industries) as local JSON files.
No database server needed, so this stays at zero cost.
"""
import json
import os
from datetime import datetime
from config import SESSIONS_DIR

os.makedirs(SESSIONS_DIR, exist_ok=True)


def _client_path(client_name: str) -> str:
    safe_name = "".join(c for c in client_name if c.isalnum() or c in ("-", "_")).lower() or "default"
    return os.path.join(SESSIONS_DIR, f"{safe_name}.json")


def _load(client_name: str) -> dict:
    path = _client_path(client_name)
    if not os.path.exists(path):
        return {"client_name": client_name, "profile": {}, "sessions": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(client_name: str, data: dict):
    with open(_client_path(client_name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_session(client_name: str, chat_history: list[dict], topics: list[str] | None = None):
    """Persist a finished conversation and roll it into the client's long-term profile."""
    data = _load(client_name)
    data["sessions"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "history": chat_history,
        "topics": topics or [],
    })

    industries = data["profile"].setdefault("frequent_topics", {})
    for t in (topics or []):
        industries[t] = industries.get(t, 0) + 1

    _save(client_name, data)


def load_client_profile(client_name: str) -> dict:
    return _load(client_name)["profile"]


def load_recent_sessions(client_name: str, limit: int = 3) -> list[dict]:
    return _load(client_name)["sessions"][-limit:]


def list_clients() -> list[str]:
    if not os.path.isdir(SESSIONS_DIR):
        return []
    return [f[:-5] for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
