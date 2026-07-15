#!/usr/bin/env python3
"""PreToolUse: deny footguns, re-read warn, optional warning systemMessage."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    emit,
    log_hook_error,
    normalize_path_key,
    plugin_data,
    read_stdin_json,
    shell_command,
    tool_input,
    tool_name,
)
from journal import append_event, count_tool_path, session_id_from_env  # noqa: E402
from policy import READ_TOOLS, evaluate, tool_path  # noqa: E402
from project_config import (  # noqa: E402
    discover_start,
    load_project_config,
    reread_warn_effective,
)


def main() -> int:
    try:
        from toggle import is_strict, is_wrath_enabled

        event = read_stdin_json()
        if not is_wrath_enabled():
            emit({"decision": "allow"})
            return 0

        data = plugin_data()
        cfg = load_project_config(discover_start(event))
        strict = is_strict(data, project=cfg)
        name = tool_name(event)
        cmd = shell_command(event)
        ti = tool_input(event)
        decision = evaluate(name, cmd, ti, config=cfg, strict=strict)

        if not decision.allow:
            try:
                append_event(
                    data,
                    {
                        "kind": "deny",
                        "session_id": session_id_from_env(event),
                        "tool": name,
                        "command": cmd[:500],
                        "path": tool_path(ti) or None,
                        "reason": decision.reason,
                    },
                )
            except Exception as exc:  # noqa: BLE001
                log_hook_error("PreToolUse.journal", exc)
            emit(decision.as_hook_dict())
            return 0

        # Soft re-read warn (allow + message)
        warning = decision.warning
        path = tool_path(ti)
        threshold = reread_warn_effective(cfg)
        if (
            threshold > 0
            and path
            and (
                name in READ_TOOLS
                or name.lower() in {t.lower() for t in READ_TOOLS}
                or name in {"read_file", "Read"}
            )
        ):
            sid = session_id_from_env(event)
            prior = count_tool_path(data, sid, path)
            # prior is past posts; this call is about to run → warn if prior+1 >= threshold
            if prior + 1 >= threshold:
                key = normalize_path_key(path)
                msg = (
                    f"Wrath: path read {prior + 1}× this session ({key!s}). "
                    "Prefer grep or skip re-read."
                )
                warning = f"{warning} {msg}".strip() if warning else msg

        out = decision.as_hook_dict()
        if warning:
            out["systemMessage"] = warning
        emit(out)
    except Exception as exc:  # noqa: BLE001 — fail-open
        log_hook_error("PreToolUse", exc)
        emit(
            {
                "decision": "allow",
                "systemMessage": f"Wrath PreToolUse error (allowed): {exc}",
            }
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
