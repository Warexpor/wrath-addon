from __future__ import annotations

from wrath.config import budget_tools_effective, discover_start, load_project_config
from wrath.event import normalize
from wrath.io import emit, ensure_mcp_config, log_hook_error, plugin_data, read_stdin_json
from wrath.journal import append_event
from wrath.modes.drive import drive_system_message
from wrath.state import (
    get_profile,
    is_il,
    is_orchestrate,
    is_privacy,
    is_strict,
    is_wrath_enabled,
    is_yolo,
)


def main() -> int:
    try:
        ensure_mcp_config()
        event = read_stdin_json()
        he = normalize(event)
        data = plugin_data()
        cfg = load_project_config(discover_start(event))
        enabled = is_wrath_enabled(data)
        strict = is_strict(data, project=cfg)
        orchestrate = is_orchestrate(data)
        il = is_il(data)
        privacy = is_privacy(data)
        yolo = is_yolo(data, project=cfg)
        profile = get_profile(data, project=cfg)
        budget = budget_tools_effective(cfg)
        append_event(
            data,
            {
                "kind": "session_start",
                "session_id": he.session_id,
                "enabled": enabled,
                "strict": strict,
                "orchestrate": orchestrate,
                "il": il,
                "privacy": privacy,
                "yolo": yolo,
                "profile": profile,
            },
        )
        emit(
            {
                "systemMessage": drive_system_message(
                    enabled=enabled,
                    strict=strict,
                    budget=budget,
                    config_path=cfg.path,
                    orchestrate=orchestrate,
                    il=il,
                    privacy=privacy,
                    yolo=yolo,
                    profile=profile,
                )
            }
        )
    except Exception as exc:  # noqa: BLE001
        log_hook_error("SessionStart", exc)
        emit({"systemMessage": f"Wrath SessionStart note: {exc}"})
    return 0
