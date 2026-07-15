#!/usr/bin/env python3
"""Stop: record turn end; soft budget nudge when tool volume is high."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import emit, plugin_data, read_stdin_json  # noqa: E402
from journal import append_event, counts, session_id_from_env  # noqa: E402

# Soft threshold — journal tools in this data dir (session-filtered when known)
BUDGET_TOOLS = 80


def main() -> int:
    try:
        from toggle import is_wrath_enabled

        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        data = plugin_data()
        sid = session_id_from_env(event)
        c = counts(data, session_id=sid if sid != "unknown" else None)
        append_event(
            data,
            {
                "kind": "stop",
                "session_id": sid,
                "reason": event.get("reason") or event.get("stopReason") or "completed",
                "counts": c,
            },
        )
        tools = int(c.get("tools") or 0)
        if tools >= BUDGET_TOOLS:
            emit(
                {
                    "systemMessage": (
                        f"Wrath budget: {tools} tool events logged this session. "
                        "Prefer grep over re-reads, /wrath-thin for small fixes, "
                        "and MCP wrath_session_stats for a histogram."
                    )
                }
            )
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
