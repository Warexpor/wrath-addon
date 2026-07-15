#!/usr/bin/env python3
"""SessionStart: inject Wrath drive pack + ensure data dir."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import emit, plugin_data, read_stdin_json  # noqa: E402
from drive_pack import drive_system_message  # noqa: E402
from journal import append_event, session_id_from_env  # noqa: E402


def main() -> int:
    try:
        event = read_stdin_json()
        data = plugin_data()
        from toggle import is_wrath_enabled  # local import after path setup

        enabled = is_wrath_enabled(data)
        append_event(
            data,
            {
                "kind": "session_start",
                "session_id": session_id_from_env(event),
                "enabled": enabled,
            },
        )
        if not enabled:
            emit(
                {
                    "systemMessage": (
                        "[Wrath mode — OFF] Guards, drive pack, and prompt nudges are disabled. "
                        "Say “turn wrath on” or run /wrath-on to re-enable. "
                        "(Plugin still loaded; only runtime flag is off.)"
                    )
                }
            )
            return 0
        emit({"systemMessage": drive_system_message()})
    except Exception as exc:  # noqa: BLE001 — fail-open
        emit({"systemMessage": f"Wrath SessionStart note: {exc}"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
