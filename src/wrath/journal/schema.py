"""Journal event kinds (schema v2)."""

from __future__ import annotations

SCHEMA_VERSION = 2

KINDS = frozenset(
    {
        "session_start",
        "session_end",
        "tool",
        "tool_fail",
        "deny",
        "harness_deny",
        "warn",
        "toggle",
        "subagent_start",
        "subagent_stop",
        "compact",
        "stop",
        "stop_fail",
        "budget",
    }
)
