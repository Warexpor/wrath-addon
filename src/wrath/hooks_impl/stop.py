from __future__ import annotations

from wrath.config import budget_tools_effective, discover_start, load_project_config
from wrath.event import normalize
from wrath.io import emit, log_hook_error, plugin_data, read_stdin_json
from wrath.journal import append_event, counts
from wrath.state import is_wrath_enabled


def main() -> int:
    try:
        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        he = normalize(event)
        data = plugin_data()
        cfg = load_project_config(discover_start(event))
        c = counts(data, session_id=he.session_id if he.session_id != "unknown" else None)
        append_event(
            data,
            {
                "kind": "stop",
                "session_id": he.session_id,
                "reason": he.reason or "completed",
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
    except Exception as exc:  # noqa: BLE001
        log_hook_error("Stop", exc)
    return 0
