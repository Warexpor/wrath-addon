#!/usr/bin/env python3
"""UserPromptSubmit: on/off + strict phrases + fluff nudge."""

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
from project_config import (  # noqa: E402
    budget_tools_effective,
    discover_start,
    load_project_config,
)
from toggle import (  # noqa: E402
    is_strict,
    is_wrath_enabled,
    parse_strict_intent,
    parse_toggle_intent,
    set_strict,
    set_wrath_enabled,
)

FLUFF = re.compile(
    r"^\s*(make it better|improve this|fix everything|do something|help|hey|hi)\s*[.!]?\s*$",
    re.I,
)


def main() -> int:
    try:
        event = read_stdin_json()
        prompt = prompt_text(event)
        data = plugin_data()
        cfg = load_project_config(discover_start(event))

        intent = parse_toggle_intent(prompt)
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
            emit(
                {
                    "systemMessage": drive_system_message(
                        enabled=state["enabled"],
                        strict=is_strict(data, project=cfg),
                        budget=budget_tools_effective(cfg),
                        config_path=cfg.path,
                    )
                }
            )
            return 0

        strict_intent = parse_strict_intent(prompt)
        if strict_intent is not None:
            state = set_strict(strict_intent, data_dir=data, source="user_prompt")
            append_event(
                data,
                {
                    "kind": "toggle",
                    "session_id": session_id_from_env(event),
                    "strict": state["strict"],
                    "source": "user_prompt_strict",
                },
            )
            emit(
                {
                    "systemMessage": (
                        f"[Wrath strict={'on' if state['strict'] else 'off'}] "
                        "Env WRATH_STRICT overrides state when set. "
                        "STRICT adds DROP/infra/force-push-without-branch blocks."
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
