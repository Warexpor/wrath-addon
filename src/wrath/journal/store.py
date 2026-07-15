"""JSONL journal under plugin data dir."""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from wrath.io import normalize_path_key
from wrath.journal.schema import SCHEMA_VERSION

DEFAULT_MAX_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_LINES = 50_000
ROTATE_KEEP = 2


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def journal_path(data_dir: Path) -> Path:
    return data_dir / "journal.jsonl"


def append_event(data_dir: Path, event: dict[str, Any]) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    path = journal_path(data_dir)
    row = {"schema": SCHEMA_VERSION, "ts": _now(), **event}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    try:
        maybe_rotate(path)
    except OSError:
        pass
    return path


def maybe_rotate(
    path: Path,
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_lines: int = DEFAULT_MAX_LINES,
) -> bool:
    if not path.is_file():
        return False
    size = path.stat().st_size
    if size < max_bytes // 4:
        return False
    if size >= max_bytes:
        _rotate(path)
        return True
    if size >= 512 * 1024:
        n = 0
        with path.open("rb") as f:
            for _ in f:
                n += 1
                if n > max_lines:
                    _rotate(path)
                    return True
    return False


def _rotate(path: Path) -> None:
    older = path.parent / f"{path.name}.{ROTATE_KEEP}"
    if older.is_file():
        older.unlink(missing_ok=True)
    for i in range(ROTATE_KEEP - 1, 0, -1):
        src = path.parent / f"{path.name}.{i}"
        dst = path.parent / f"{path.name}.{i + 1}"
        if src.is_file():
            src.replace(dst)
    first = path.parent / f"{path.name}.1"
    if path.is_file():
        path.replace(first)


def _iter_tail_lines(path: Path, n: int) -> list[str]:
    n = max(int(n), 1)
    if not path.is_file():
        return []
    size = path.stat().st_size
    if size == 0:
        return []
    if size < 256 * 1024:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return [ln for ln in lines if ln.strip()][-n:]
    block = 64 * 1024
    data = b""
    with path.open("rb") as f:
        pos = size
        while pos > 0 and data.count(b"\n") <= n + 2:
            read_size = min(block, pos)
            pos -= read_size
            f.seek(pos)
            data = f.read(read_size) + data
            if pos == 0:
                break
    text = data.decode("utf-8", errors="replace")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return lines[-n:]


def tail(
    data_dir: Path,
    n: int = 20,
    *,
    kind: str | None = None,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    path = journal_path(data_dir)
    fetch = n * 5 if (kind or session_id) else n
    raw_lines = _iter_tail_lines(path, fetch)
    out: list[dict[str, Any]] = []
    for line in raw_lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            row = {"raw": line}
        if kind and row.get("kind") != kind and row.get("type") != kind:
            continue
        if session_id and str(row.get("session_id") or "") != session_id:
            continue
        out.append(row)
    return out[-max(n, 1) :]


def last_denies(data_dir: Path, n: int = 10, *, session_id: str | None = None) -> list[dict]:
    rows = tail(data_dir, n=max(n * 8, 40), session_id=session_id)
    out: list[dict] = []
    for row in reversed(rows):
        kind = row.get("kind") or row.get("type")
        if kind in ("deny", "harness_deny"):
            out.append(row)
            if len(out) >= n:
                break
    return list(reversed(out))


def counts(data_dir: Path, *, session_id: str | None = None) -> dict[str, int]:
    path = journal_path(data_dir)
    if not path.is_file():
        return {
            "events": 0,
            "tools": 0,
            "stops": 0,
            "denies": 0,
            "toggles": 0,
            "subagents": 0,
        }
    events = tools = stops = denies = toggles = subagents = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip():
                continue
            events += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if session_id and str(row.get("session_id") or "") != session_id:
                events -= 1
                continue
            kind = row.get("kind") or row.get("type")
            if kind == "tool":
                tools += 1
            elif kind == "stop":
                stops += 1
            elif kind in ("deny", "harness_deny"):
                denies += 1
            elif kind == "toggle":
                toggles += 1
            elif kind == "subagent_start":
                subagents += 1
    return {
        "events": events,
        "tools": tools,
        "stops": stops,
        "denies": denies,
        "toggles": toggles,
        "subagents": subagents,
    }


def session_stats(data_dir: Path, session_id: str, top_tools: int = 8) -> dict[str, Any]:
    path = journal_path(data_dir)
    c: Counter[str] = Counter()
    denies: list[dict[str, Any]] = []
    events = 0
    if path.is_file():
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if str(row.get("session_id") or "") != session_id:
                    continue
                events += 1
                kind = row.get("kind") or row.get("type")
                if kind == "tool":
                    c[str(row.get("tool") or "unknown")] += 1
                elif kind in ("deny", "harness_deny"):
                    denies.append(
                        {
                            "tool": row.get("tool"),
                            "reason": row.get("reason"),
                            "rule_id": row.get("rule_id"),
                            "ts": row.get("ts"),
                            "kind": kind,
                        }
                    )
    return {
        "session_id": session_id,
        "events": events,
        "tool_histogram": dict(c.most_common(top_tools)),
        "denies": denies[-15:],
        "deny_count": len(denies),
    }


def session_id_from_env(event: dict[str, Any] | None = None) -> str:
    if event:
        sid = event.get("sessionId") or event.get("session_id")
        if sid:
            return str(sid)
    return os.environ.get("GROK_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID") or "unknown"


def count_tool_path(
    data_dir: Path,
    session_id: str,
    path: str,
    *,
    kind: str = "tool",
) -> int:
    """Prefer session counter sidecar; fall back to journal scan."""
    key = normalize_path_key(path)
    if not key:
        return 0
    # sidecar
    try:
        from wrath.counters import get_path_count

        n = get_path_count(data_dir, session_id, key)
        if n is not None:
            return n
    except Exception:
        pass
    jp = journal_path(data_dir)
    if not jp.is_file():
        return 0
    n = 0
    with jp.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (row.get("kind") or row.get("type")) != kind:
                continue
            if session_id and session_id != "unknown":
                if str(row.get("session_id") or "") != session_id:
                    continue
            if normalize_path_key(str(row.get("path") or "")) == key:
                n += 1
    return n
