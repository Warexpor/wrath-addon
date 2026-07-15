from __future__ import annotations

from wrath.event import normalize
from wrath.io import log_hook_error, plugin_data, read_stdin_json
from wrath.journal import append_event
from wrath.state import is_wrath_enabled


def main() -> int:
    try:
        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        he = normalize(event)
        append_event(
            plugin_data(),
            {
                "kind": "harness_deny",
                "session_id": he.session_id,
                "tool": he.tool_name,
                "command": (he.shell_command or "")[:300] or None,
                "path": he.path() or None,
                "reason": (he.reason or "permission denied")[:500],
                "rule_id": "harness",
            },
        )
    except Exception as exc:  # noqa: BLE001
        log_hook_error("PermissionDenied", exc)
    return 0
