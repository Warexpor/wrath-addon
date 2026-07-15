from __future__ import annotations

from wrath.event import normalize
from wrath.io import log_hook_error, plugin_data, read_stdin_json
from wrath.journal import append_event, counts
from wrath.state import is_wrath_enabled


def main() -> int:
    try:
        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        he = normalize(event)
        data = plugin_data()
        c = counts(data, session_id=he.session_id if he.session_id != "unknown" else None)
        append_event(
            data,
            {
                "kind": "session_end",
                "session_id": he.session_id,
                "counts": c,
            },
        )
    except Exception as exc:  # noqa: BLE001
        log_hook_error("SessionEnd", exc)
    return 0
