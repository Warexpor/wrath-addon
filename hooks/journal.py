"""JSONL journal under plugin data dir (efficient tail, rotation, session stats)."""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Soft caps — keep disk use bounded without external deps
DEFAULT_MAX_BYTES = 8 * 1024 * 1024  # 8 MiB
DEFAULT_MAX_LINES = 50_000
ROTATE_KEEP = 2


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def journal_path(data_dir: Path) -> Path:
    return data_dir / "journal.jsonl"


def append_event(data_dir: Path, event: dict[str, Any]) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    path = journal_path(data_dir)
    row = {"ts": _now(), **event}
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
    """Rotate journal if over size/line caps. Returns True if rotated."""
    if not path.is_file():
        return False
    size = path.stat().st_size
    if size < max_bytes:
        # cheap line estimate: only count when large-ish
        if size < max_bytes // 4:
            return False
    # Always check when over quarter of max_bytes or explicitly oversized
    if size >= max_bytes:
        _rotate(path)
        return True
    # Line count only if moderately large
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
    # journal.jsonl -> journal.jsonl.1; journal.jsonl.1 -> journal.jsonl.2
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
    """Return last n non-empty-stripped lines efficiently for large files."""
    n = max(int(n), 1)
    if not path.is_file():
        return []
    size = path.stat().st_size
    if size == 0:
        return []
    # Small file: simple path
    if size < 256 * 1024:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return [ln for ln in lines if ln.strip()][-n:]

    # Read from end in chunks
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
    # Over-fetch if filtering
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


def counts(data_dir: Path, *, session_id: str | None = None) -> dict[str, int]:
    path = journal_path(data_dir)
    if not path.is_file():
        return {"events": 0, "tools": 0, "stops": 0, "denies": 0, "toggles": 0}
    events = tools = stops = denies = toggles = 0
    # Stream whole file for accurate counts (rotated files stay small)
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
            elif kind == "deny":
                denies += 1
            elif kind == "toggle":
                toggles += 1
    return {
        "events": events,
        "tools": tools,
        "stops": stops,
        "denies": denies,
        "toggles": toggles,
    }


def session_stats(data_dir: Path, session_id: str, top_tools: int = 8) -> dict[str, Any]:
    path = journal_path(data_dir)
    c = Counter()
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
                elif kind == "deny":
                    denies.append(
                        {
                            "tool": row.get("tool"),
                            "reason": row.get("reason"),
                            "ts": row.get("ts"),
                        }
                    )
    return {
        "session_id": session_id,
        "events": events,
        "tool_histogram": dict(c.most_common(top_tools)),
        "denies": denies[-10:],
        "deny_count": len(denies),
    }


def session_id_from_env(event: dict[str, Any] | None = None) -> str:
    if event:
        sid = event.get("sessionId") or event.get("session_id")
        if sid:
            return str(sid)
    return os.environ.get("GROK_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID") or "unknown"
