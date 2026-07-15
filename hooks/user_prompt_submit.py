#!/usr/bin/env python3
"""UserPromptSubmit: toggle on/off phrases + rare fluff nudge (when enabled)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    emit,
    log_hook_error,
    plugin_data,
    prompt_text,
    read_stdin_json,
)
from drive_pack import drive_system_message  # noqa: E402
from journal import append_event, session_id_from_env  # noqa: E402
from toggle import is_wrath_enabled, parse_toggle_intent, set_wrath_enabled  # noqa: E402

FLUFF = re.compile(
    r"^\s*(make it better|improve this|fix everything|do something|help|hey|hi)\s*[.!]?\s*$",
    re.I,
)


def main() -> int:
    try:
        event = read_stdin_json()
        prompt = prompt_text(event)
        intent = parse_toggle_intent(prompt)
        data = plugin_data()

        if intent is not None:
            state = set_wrath_enabled(intent, data_dir=data, source="user_prompt")
            append_event(
                data,
                {
                    "kind": "toggle",
                    "session_id": session_id_from_env(event),
                    "enabled": state["enabled"],
                    "source": "user_prompt",
                },
            )
            if state["enabled"]:
                emit({"systemMessage": drive_system_message()})
            else:
                emit(
                    {
                        "systemMessage": (
                            "[Wrath OFF] Guards and drive nudges disabled until you turn Wrath on. "
                            "Plugin remains installed. /wrath-on or “turn wrath on” to re-enable."
                        )
                    }
                )
            return 0

        if not is_wrath_enabled(data):
            return 0

        if FLUFF.match(prompt.strip()):
            emit(
                {
                    "systemMessage": (
                        "Wrath: prompt is underspecified. Ask for the concrete target "
                        "(path + desired outcome) or run /wrath-thin with a real task."
                    )
                }
            )
            return 0
    except Exception as exc:  # noqa: BLE001 — fail-open
        log_hook_error("UserPromptSubmit", exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
