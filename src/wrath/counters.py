"""Per-session path counters (fast re-read warns without full journal scan)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _path(data_dir: Path, session_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (session_id or "unknown"))[:80]
    d = data_dir / "session_counters"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{safe}.json"


def _load(data_dir: Path, session_id: str) -> dict[str, Any]:
    p = _path(data_dir, session_id)
    if not p.is_file():
        return {"paths": {}, "fails": 0}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            raw.setdefault("paths", {})
            raw.setdefault("fails", 0)
            return raw
    except (OSError, json.JSONDecodeError):
        pass
    return {"paths": {}, "fails": 0}


def _save(data_dir: Path, session_id: str, data: dict[str, Any]) -> None:
    p = _path(data_dir, session_id)
    p.write_text(json.dumps(data), encoding="utf-8")


def bump_path(data_dir: Path, session_id: str, path_key: str) -> int:
    data = _load(data_dir, session_id)
    paths: dict[str, int] = data.setdefault("paths", {})
    n = int(paths.get(path_key, 0)) + 1
    paths[path_key] = n
    # bound map size
    if len(paths) > 500:
        # drop lowest counts
        for k, _ in sorted(paths.items(), key=lambda kv: kv[1])[:100]:
            paths.pop(k, None)
    _save(data_dir, session_id, data)
    return n


def get_path_count(data_dir: Path, session_id: str, path_key: str) -> int | None:
    data = _load(data_dir, session_id)
    paths = data.get("paths") or {}
    if path_key not in paths and not paths:
        return None  # no sidecar yet → fall back to journal
    return int(paths.get(path_key, 0))


def bump_fail(data_dir: Path, session_id: str) -> int:
    data = _load(data_dir, session_id)
    n = int(data.get("fails", 0)) + 1
    data["fails"] = n
    _save(data_dir, session_id, data)
    return n


def get_fails(data_dir: Path, session_id: str) -> int:
    return int(_load(data_dir, session_id).get("fails", 0))
