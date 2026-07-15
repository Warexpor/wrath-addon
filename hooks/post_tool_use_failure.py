#!/usr/bin/env python3
"""PostToolUseFailure: journal failed tool calls (never blocks)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    log_hook_error,
    plugin_data,
    read_stdin_json,
    shell_command,
    tool_name,
)
from journal import append_event, session_id_from_env  # noqa: E402


def main() -> int:
    try:
        from toggle import is_wrath_enabled

        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        err = event.get("error") or event.get("message") or event.get("errorMessage") or ""
        append_event(
            plugin_data(),
            {
                "kind": "tool_fail",
                "session_id": session_id_from_env(event),
                "tool": tool_name(event),
                "command": (shell_command(event) or "")[:300] or None,
                "error": str(err)[:400],
            },
        )
    except Exception as exc:  # noqa: BLE001 — fail-open
        log_hook_error("PostToolUseFailure", exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
