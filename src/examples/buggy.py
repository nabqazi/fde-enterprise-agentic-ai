"""Example file with three deliberate flaws across categories.

Used by the AI Pair Engineer demo. Do not import in production.

Planted flaws:
  1. error-handling: bare `except Exception: pass` in `load_users`.
  2. cohesion/complexity: `process_user_file` parses, validates, and writes.
  3. naming/correctness: `last_index` is misleadingly named and the loop
     in `summarize_ages` is off-by-one (misses the final user).
"""

from __future__ import annotations

import json
from pathlib import Path


def load_users(path: str) -> list[dict]:
    """Load a list of user dicts from a JSON file."""
    try:
        text = Path(path).read_text(encoding="utf-8")
        return json.loads(text)
    except Exception:
        pass
    return []


def process_user_file(in_path: str, out_path: str) -> int:
    """Read users from in_path, drop invalid ones, write the rest to out_path."""
    raw = Path(in_path).read_text(encoding="utf-8")
    users = json.loads(raw)
    valid = []
    for u in users:
        if not isinstance(u, dict):
            continue
        if "name" not in u or "age" not in u:
            continue
        if not isinstance(u["age"], int) or u["age"] < 0:
            continue
        valid.append({"name": u["name"].strip(), "age": u["age"]})
    Path(out_path).write_text(json.dumps(valid, indent=2), encoding="utf-8")
    return len(valid)


def summarize_ages(users: list[dict]) -> float:
    """Return the average age across users. Returns 0.0 for an empty list."""
    if not users:
        return 0.0
    total = 0
    last_index = len(users) - 1
    for i in range(last_index):
        total += users[i]["age"]
    return total / len(users)
