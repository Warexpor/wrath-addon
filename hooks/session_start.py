#!/usr/bin/env python3
"""SessionStart: status line + drive pack."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import emit, ensure_mcp_config, log_hook_error, plugin_data, read_stdin_json  # noqa: E402
from drive_pack import drive_system_message  # noqa: E402
from journal import append_event, session_id_from_env  # noqa: E402
from project_config import (  # noqa: E402
    budget_tools_effective,
    discover_start,
    load_project_config,
)


def main() -> int:
    try:
        ensure_mcp_config()
        event = read_stdin_json()
        data = plugin_data()
        from toggle import is_il, is_orchestrate, is_strict, is_wrath_enabled

        cfg = load_project_config(discover_start(event))
        enabled = is_wrath_enabled(data)
        strict = is_strict(data, project=cfg)
        orchestrate = is_orchestrate(data)
        il = is_il(data)
        budget = budget_tools_effective(cfg)
        append_event(
            data,
            {
                "kind": "session_start",
                "session_id": session_id_from_env(event),
                "enabled": enabled,
                "strict": strict,
                "orchestrate": orchestrate,
                "il": il,
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
                )
            }
        )
    except Exception as exc:  # noqa: BLE001 — fail-open
        log_hook_error("SessionStart", exc)
        emit({"systemMessage": f"Wrath SessionStart note: {exc}"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
