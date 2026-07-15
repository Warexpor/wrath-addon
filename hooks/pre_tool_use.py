#!/usr/bin/env python3
"""PreToolUse: deny footguns, optional warning systemMessage."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    emit,
    log_hook_error,
    plugin_data,
    read_stdin_json,
    shell_command,
    tool_input,
    tool_name,
)
from journal import append_event, session_id_from_env  # noqa: E402
from policy import evaluate  # noqa: E402


def main() -> int:
    try:
        from toggle import is_wrath_enabled

        event = read_stdin_json()  # always drain stdin
        if not is_wrath_enabled():
            emit({"decision": "allow"})
            return 0
        name = tool_name(event)
        cmd = shell_command(event)
        ti = tool_input(event)
        decision = evaluate(name, cmd, ti)
        if not decision.allow:
            try:
                append_event(
                    plugin_data(),
                    {
                        "kind": "deny",
                        "session_id": session_id_from_env(event),
                        "tool": name,
                        "command": cmd[:500],
                        "reason": decision.reason,
                    },
                )
            except Exception as exc:  # noqa: BLE001
                log_hook_error("PreToolUse.journal", exc)
        emit(decision.as_hook_dict())
    except Exception as exc:  # noqa: BLE001 — fail-open
        log_hook_error("PreToolUse", exc)
        emit(
            {
                "decision": "allow",
                "systemMessage": f"Wrath PreToolUse error (allowed): {exc}",
            }
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
