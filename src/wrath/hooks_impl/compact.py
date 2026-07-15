from __future__ import annotations

from wrath.config import budget_tools_effective, discover_start, load_project_config
from wrath.event import normalize
from wrath.io import emit, log_hook_error, plugin_data, read_stdin_json
from wrath.journal import append_event, counts
from wrath.state import is_wrath_enabled


def main_pre() -> int:
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
            {"kind": "compact", "session_id": he.session_id, "phase": "pre", "counts": c},
        )
        emit(
            {
                "systemMessage": (
                    f"Wrath: compacting context (tools={c.get('tools', 0)}, "
                    f"budget={budget_tools_effective(cfg)}). "
                    "Keep next turns tight; /wrath-thin if scope bloated."
                )
            }
        )
    except Exception as exc:  # noqa: BLE001
        log_hook_error("PreCompact", exc)
    return 0


def main_post() -> int:
    try:
        event = read_stdin_json()
        if not is_wrath_enabled():
            return 0
        he = normalize(event)
        append_event(
            plugin_data(),
            {"kind": "compact", "session_id": he.session_id, "phase": "post"},
        )
    except Exception as exc:  # noqa: BLE001
        log_hook_error("PostCompact", exc)
    return 0
