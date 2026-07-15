"""Policy engine — ordered rules, shared by hooks + MCP."""

from __future__ import annotations

from wrath.config import EffectiveConfig, nested_depth_effective
from wrath.event import canonicalize_tool
from wrath.io import split_shell_segments
from wrath.policy.decision import Decision
from wrath.policy.rules.privacy_upload import check_privacy_upload
from wrath.policy.rules.project_deny import check_project_deny
from wrath.policy.rules.secrets import check_secret_url, check_secret_write
from wrath.policy.rules.shell_destructive import check_destructive
from wrath.policy.rules.shell_git import check_git
from wrath.policy.rules.shell_infra import check_infra
from wrath.policy.rules.shell_nested import fully_unwrap, unwrap_nested_shell
from wrath.policy.rules.shell_pipe_exec import check_pipe_exec
from wrath.policy.rules.spawn_orch import check_spawn_model
from wrath.policy.rules.write_guard import check_write_git, path_is_git_internal

SHELL_TOOLS = {
    "run_terminal_command",
    "Bash",
    "bash",
    "Shell",
    "shell",
    "terminal",
    "run_command",
}

WRITE_TOOLS = {
    "write",
    "Write",
    "search_replace",
    "Edit",
    "edit",
    "create_file",
    "WriteFile",
    "str_replace",
}

READ_TOOLS = {
    "read_file",
    "Read",
    "read",
    "open_page",
    "ReadFile",
}


def tool_path(tool_input: dict | None) -> str:
    tool_input = tool_input or {}
    return str(
        tool_input.get("path")
        or tool_input.get("file_path")
        or tool_input.get("target_file")
        or tool_input.get("target_directory")
        or ""
    )


def evaluate(
    tool: str,
    command: str = "",
    tool_input: dict | None = None,
    *,
    config: EffectiveConfig | None = None,
    strict: bool | None = None,
    orchestrate: bool = False,
    privacy: bool = False,
    yolo: bool = False,
) -> Decision:
    tool_input = tool_input or {}
    raw_name = (tool or "").strip()
    name = canonicalize_tool(raw_name) or raw_name
    cmd = (command or "").strip()
    # yolo: opposite of max — no strict, no privacy bulk, soft allow footguns
    if yolo:
        privacy = False
        use_strict = False
    else:
        use_strict = bool(strict) if strict is not None else bool(config and config.strict)

    # Spawn orch gate (non-shell) — keep first warn Decision for rule_id
    spawn_mode = "off"
    if config:
        spawn_mode = config.require_spawn_model
    if yolo:
        spawn_mode = "off"
    elif orchestrate and spawn_mode == "off":
        spawn_mode = "warn"
    # Check both raw and canonical names (Task vs spawn_subagent)
    spawn_d = check_spawn_model(raw_name, tool_input, orchestrate=orchestrate, mode=spawn_mode)
    if spawn_d is None and name != raw_name:
        spawn_d = check_spawn_model(name, tool_input, orchestrate=orchestrate, mode=spawn_mode)
    if spawn_d and not spawn_d.allow:
        return spawn_d
    warn_dec: Decision | None = spawn_d if (spawn_d and spawn_d.warning) else None

    if (
        name in SHELL_TOOLS
        or raw_name in SHELL_TOOLS
        or name.lower()
        in {
            "bash",
            "shell",
            "terminal",
        }
    ):
        shell_d = _eval_shell(
            cmd,
            config=config,
            strict=use_strict,
            privacy=privacy,
            yolo=yolo,
        )
        if not shell_d.allow:
            return shell_d
        if shell_d.warning and warn_dec is None:
            warn_dec = shell_d
        if warn_dec is not None:
            return warn_dec
        return shell_d

    path = tool_path(tool_input)

    if (
        name in WRITE_TOOLS
        or raw_name in WRITE_TOOLS
        or name.lower() in {t.lower() for t in WRITE_TOOLS}
    ):
        wg = check_write_git(path)
        if wg:
            return wg

    sec = check_secret_write(path, tool_input)
    if sec:
        if not sec.allow:
            return sec
        if sec.warning and warn_dec is None:
            warn_dec = sec

    su = check_secret_url(tool_input)
    if su and not su.allow:
        return su

    if warn_dec is not None:
        return warn_dec
    return Decision(allow=True)


def _eval_shell(
    cmd: str,
    *,
    config: EffectiveConfig | None,
    strict: bool,
    privacy: bool,
    yolo: bool = False,
) -> Decision:
    if not cmd:
        return Decision(allow=True)

    depth = nested_depth_effective(config)
    # Evaluate every unwrap layer + segments of original
    layers = fully_unwrap(cmd, max_depth=depth)
    warn_dec: Decision | None = None

    privacy_mode = "warn"
    if config:
        privacy_mode = config.privacy_upload
    if yolo:
        privacy_mode = "off"
    elif privacy and privacy_mode == "warn":
        privacy_mode = "deny"

    for layer in layers:
        for seg in split_shell_segments(layer):
            d = _eval_shell_segment(seg, strict=strict, privacy_mode=privacy_mode, yolo=yolo)
            if not d.allow:
                return d
            if d.warning and warn_dec is None:
                warn_dec = d

    # Project deny always applies (even yolo) — explicit repo red lines.
    pd = check_project_deny(cmd, config)
    if pd:
        return pd

    if warn_dec is not None:
        return warn_dec
    return Decision(allow=True)


def _eval_shell_segment(
    cmd: str, *, strict: bool, privacy_mode: str, yolo: bool = False
) -> Decision:
    # Catastrophic fs always checked first.
    d = check_destructive(cmd)
    if d is not None:
        if not d.allow:
            return d
        # warn-only destructive (chmod 777, rm -rf subdir)
        if not yolo:
            rest = _eval_shell_segment_denies_only(cmd, strict=strict, yolo=False)
            if rest and not rest.allow:
                return rest
            return d
        # yolo: keep warn, skip soft footgun denials below
        return d

    if yolo:
        # Soft footguns allowed under yolo; privacy already off.
        return Decision(allow=True)

    for fn in (
        lambda c: check_pipe_exec(c),
        lambda c: check_git(c, strict=strict),
        lambda c: check_infra(c, strict=strict),
        lambda c: check_privacy_upload(c, mode=privacy_mode),
    ):
        d2 = fn(cmd)
        if d2 is not None:
            if not d2.allow:
                return d2
            rest = _eval_shell_segment_denies_only(cmd, strict=strict, yolo=False)
            if rest and not rest.allow:
                return rest
            return d2
    return Decision(allow=True)


def _eval_shell_segment_denies_only(
    cmd: str, *, strict: bool, yolo: bool = False
) -> Decision | None:
    if yolo:
        d = check_destructive(cmd)
        if d is not None and not d.allow:
            return d
        return None
    for fn in (
        lambda c: check_destructive(c),
        lambda c: check_pipe_exec(c),
        lambda c: check_git(c, strict=strict),
        lambda c: check_infra(c, strict=strict),
    ):
        d = fn(cmd)
        if d is not None and not d.allow:
            return d
    return None


# re-export path helper
__all__ = [
    "Decision",
    "READ_TOOLS",
    "SHELL_TOOLS",
    "WRITE_TOOLS",
    "evaluate",
    "path_is_git_internal",
    "tool_path",
    "unwrap_nested_shell",
]
