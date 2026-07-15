#!/usr/bin/env python3
"""Stop: record turn end; soft budget nudge when tool volume is high."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import emit, log_hook_error, plugin_data, read_stdin_json  # noqa: E402
from journal import append_event, counts, session_id_from_env  # noqa: E402
from project_config import budget_tools_effective, discover_start, load_project_config  # noqa: E402


def main() -> int:
    try:
        from toggle import is_wrath_enabled

        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        data = plugin_data()
        cfg = load_project_config(discover_start(event))
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
        threshold = budget_tools_effective(cfg)
        if tools >= threshold:
            emit(
                {
                    "systemMessage": (
                        f"Wrath budget: {tools} tool events this session "
                        f"(threshold {threshold}). "
                        "Prefer grep over re-reads; /wrath-thin; MCP wrath_session_stats."
                    )
                }
            )
    except Exception as exc:  # noqa: BLE001 — fail-open
        log_hook_error("Stop", exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
