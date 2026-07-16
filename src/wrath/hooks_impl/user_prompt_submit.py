from __future__ import annotations

import re

from wrath.config import budget_tools_effective, discover_start, load_project_config
from wrath.event import normalize
from wrath.io import emit, log_hook_error, plugin_data, read_stdin_json
from wrath.journal import append_event
from wrath.modes.drive import drive_system_message
from wrath.modes.orchestrate import ORCHESTRATE_BODY
from wrath.modes.privacy import PRIVACY_BODY
from wrath.modes.yolo import YOLO_BODY
from wrath.state import (
    get_profile,
    is_orchestrate,
    is_privacy,
    is_strict,
    is_wrath_enabled,
    is_yolo,
    parse_orchestrate_intent,
    parse_privacy_intent,
    parse_profile_intent,
    parse_strict_intent,
    parse_toggle_intent,
    parse_yolo_intent,
    set_orchestrate,
    set_privacy,
    set_profile,
    set_strict,
    set_wrath_enabled,
    set_yolo,
)

FLUFF = re.compile(
    r"^\s*(make it better|improve this|fix everything|do something|help|hey|hi)\s*[.!]?\s*$",
    re.I,
)


def main() -> int:
    try:
        event = read_stdin_json()
        he = normalize(event)
        prompt = he.prompt
        data = plugin_data()
        cfg = load_project_config(discover_start(event))

        prof = parse_profile_intent(prompt)
        if prof is not None:
            state = set_profile(prof, data_dir=data, source="user_prompt")
            append_event(
                data,
                {
                    "kind": "toggle",
                    "session_id": he.session_id,
                    "profile": state.get("profile"),
                    "source": "user_prompt_profile",
                },
            )
            emit(
                {
                    "systemMessage": drive_system_message(
                        enabled=is_wrath_enabled(data),
                        strict=is_strict(data, project=cfg),
                        budget=budget_tools_effective(cfg),
                        config_path=cfg.path,
                        orchestrate=is_orchestrate(data),
                        privacy=is_privacy(data),
                        yolo=is_yolo(data, project=cfg),
                        profile=str(state.get("profile") or prof),
                    )
                }
            )
            return 0

        yolo_intent = parse_yolo_intent(prompt)
        if yolo_intent is not None:
            state = set_yolo(yolo_intent, data_dir=data, source="user_prompt")
            append_event(
                data,
                {
                    "kind": "toggle",
                    "session_id": he.session_id,
                    "yolo": state.get("yolo"),
                    "profile": state.get("profile"),
                    "source": "user_prompt_yolo",
                },
            )
            on = bool(state.get("yolo"))
            msg = f"[Wrath yolo={'on' if on else 'off'}] Env WRATH_YOLO overrides state."
            if on:
                msg = f"{msg}\n{YOLO_BODY.strip()}"
            emit({"systemMessage": msg})
            return 0

        priv = parse_privacy_intent(prompt)
        if priv is not None:
            state = set_privacy(priv, data_dir=data, source="user_prompt")
            append_event(
                data,
                {
                    "kind": "toggle",
                    "session_id": he.session_id,
                    "privacy": state["privacy"],
                    "source": "user_prompt_privacy",
                },
            )
            on = bool(state["privacy"])
            msg = f"[Wrath privacy={'on' if on else 'off'}] Env WRATH_PRIVACY overrides state."
            if on:
                msg = f"{msg}\n{PRIVACY_BODY.strip()}"
            emit({"systemMessage": msg})
            return 0

        orch_intent = parse_orchestrate_intent(prompt)
        if orch_intent is not None:
            state = set_orchestrate(orch_intent, data_dir=data, source="user_prompt")
            append_event(
                data,
                {
                    "kind": "toggle",
                    "session_id": he.session_id,
                    "orchestrate": state["orchestrate"],
                    "source": "user_prompt_orchestrate",
                },
            )
            on = bool(state["orchestrate"])
            msg = (
                f"[Wrath orchestrate={'on' if on else 'off'}] "
                "Env WRATH_ORCHESTRATE overrides state when set."
            )
            if on:
                msg = f"{msg}\n{ORCHESTRATE_BODY.strip()}"
            else:
                msg = f"{msg} Style dispatch routing disabled for this machine."
            emit({"systemMessage": msg})
            return 0

        strict_intent = parse_strict_intent(prompt)
        if strict_intent is not None:
            state = set_strict(strict_intent, data_dir=data, source="user_prompt")
            append_event(
                data,
                {
                    "kind": "toggle",
                    "session_id": he.session_id,
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

        intent = parse_toggle_intent(prompt)
        if intent is not None:
            state = set_wrath_enabled(intent, data_dir=data, source="user_prompt")
            append_event(
                data,
                {
                    "kind": "toggle",
                    "session_id": he.session_id,
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
                        orchestrate=is_orchestrate(data),
                        privacy=is_privacy(data),
                        yolo=is_yolo(data, project=cfg),
                        profile=get_profile(data, project=cfg),
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
    except Exception as exc:
        log_hook_error("UserPromptSubmit", exc)
    return 0
