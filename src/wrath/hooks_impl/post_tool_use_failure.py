from __future__ import annotations

from wrath.counters import bump_fail, get_fails
from wrath.event import normalize
from wrath.io import emit, log_hook_error, plugin_data, read_stdin_json
from wrath.journal import append_event
from wrath.state import is_wrath_enabled


def main() -> int:
    try:
        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        he = normalize(event)
        data = plugin_data()
        n = bump_fail(data, he.session_id)
        append_event(
            data,
            {
                "kind": "tool_fail",
                "session_id": he.session_id,
                "tool": he.tool_name,
                "command": (he.shell_command or "")[:300] or None,
                "reason": (he.reason or "")[:300] or None,
                "fails": n,
            },
        )
        if n >= 5 and get_fails(data, he.session_id) >= 5:
            emit(
                {
                    "systemMessage": (
                        f"Wrath: {n} tool failures this session — "
                        "stop retry loops; change approach or /wrath-check."
                    )
                }
            )
    except Exception as exc:  # noqa: BLE001
        log_hook_error("PostToolUseFailure", exc)
    return 0
