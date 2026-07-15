#!/usr/bin/env python3
"""PostToolUse: journal tool activity (never blocks)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
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
        name = tool_name(event)
        cmd = shell_command(event)
        append_event(
            plugin_data(),
            {
                "kind": "tool",
                "session_id": session_id_from_env(event),
                "tool": name,
                "command": (cmd or "")[:300] or None,
            },
        )
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
