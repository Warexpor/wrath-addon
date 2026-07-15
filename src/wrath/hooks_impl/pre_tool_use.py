from __future__ import annotations

from wrath.config import (
    discover_start,
    load_project_config,
    reread_warn_effective,
)
from wrath.counters import bump_path
from wrath.event import normalize
from wrath.io import (
    emit,
    log_hook_error,
    normalize_path_key,
    plugin_data,
    read_stdin_json,
)
from wrath.journal import append_event, count_tool_path
from wrath.policy import READ_TOOLS, evaluate
from wrath.state import is_orchestrate, is_privacy, is_strict, is_wrath_enabled


def main() -> int:
    try:
        event = read_stdin_json()
        he = normalize(event)
        data = plugin_data()
        if not is_wrath_enabled(data):
            emit({"decision": "allow"})
            return 0

        cfg = load_project_config(discover_start(event))
        strict = is_strict(data, project=cfg)
        orch = is_orchestrate(data)
        privacy = is_privacy(data)
        name = he.tool_name
        cmd = he.shell_command
        ti = he.tool_input
        decision = evaluate(
            name,
            cmd,
            ti,
            config=cfg,
            strict=strict,
            orchestrate=orch,
            privacy=privacy,
        )

        if not decision.allow:
            try:
                append_event(
                    data,
                    {
                        "kind": "deny",
                        "session_id": he.session_id,
                        "tool": name,
                        "command": cmd[:500],
                        "path": he.path() or None,
                        "reason": decision.reason,
                        "rule_id": decision.rule_id or None,
                    },
                )
            except Exception as exc:  # noqa: BLE001
                log_hook_error("PreToolUse.journal", exc)
            emit(decision.as_hook_dict())
            return 0

        warning = decision.warning
        path = he.path()
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
            key = normalize_path_key(path)
            try:
                prior = bump_path(data, he.session_id, key) - 1
            except Exception:
                prior = count_tool_path(data, he.session_id, path)
            if prior + 1 >= threshold:
                msg = (
                    f"Wrath: path read {prior + 1}× this session ({key!s}). "
                    "Prefer grep or skip re-read."
                )
                warning = f"{warning} {msg}".strip() if warning else msg

        out = decision.as_hook_dict()
        if warning:
            out["systemMessage"] = warning
        emit(out)
    except Exception as exc:  # noqa: BLE001
        log_hook_error("PreToolUse", exc)
        emit(
            {
                "decision": "allow",
                "systemMessage": f"Wrath PreToolUse error (allowed): {exc}",
            }
        )
    return 0
