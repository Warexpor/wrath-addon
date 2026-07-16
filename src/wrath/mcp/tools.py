"""MCP tool handlers for Wrath V2."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from wrath.config import (
    budget_tools_effective,
    discover_start,
    load_project_config,
    reread_warn_effective,
)
from wrath.io import plugin_version
from wrath.journal import counts, journal_path, last_denies, session_stats, tail
from wrath.policy import evaluate
from wrath.state import (
    get_profile,
    is_orchestrate,
    is_privacy,
    is_strict,
    is_wrath_enabled,
    is_yolo,
    load_state,
    set_orchestrate,
    set_privacy,
    set_profile,
    set_wrath_enabled,
    set_yolo,
)


def data_dir() -> Path:
    raw = os.environ.get("GROK_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if raw:
        p = Path(raw)
    else:
        p = Path.home() / ".wrath-addon" / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _mcp_health(root: Path) -> dict[str, Any]:
    mcp_json = root / ".mcp.json"
    launcher = root / "mcp" / "launch.cmd"
    if not launcher.is_file():
        launcher = root / "mcp" / "run.py"
    absolute = False
    args: list = []
    command = ""
    exists = launcher.is_file()
    fix = None
    if mcp_json.is_file():
        try:
            cfg = json.loads(mcp_json.read_text(encoding="utf-8"))
            servers = cfg.get("mcpServers") or cfg.get("mcp_servers") or {}
            wrath = servers.get("wrath") or {}
            command = str(wrath.get("command") or "")
            args = list(wrath.get("args") or [])
            candidate: Path | None = None
            if command and not command.lower().startswith("python"):
                candidate = Path(command)
            elif args:
                candidate = Path(str(args[0]))
            if candidate is not None:
                absolute = candidate.is_absolute()
                if absolute:
                    exists = candidate.is_file()
                else:
                    exists = (root / candidate).is_file()
        except (OSError, json.JSONDecodeError, TypeError):
            fix = r".\install.ps1  # re-patch absolute MCP launcher"
    if not absolute or not exists:
        fix = r".\install.ps1  # re-patch absolute MCP launcher"
    return {
        "mcp_json": mcp_json.is_file(),
        "mcp_command": command,
        "mcp_args": args,
        "mcp_args_absolute": absolute,
        "mcp_run_exists": exists,
        "fix": fix,
    }


TOOLS = [
    {
        "name": "wrath_status",
        "description": "One-shot Wrath status (modes, profile, budget, config).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "wrath_journal_tail",
        "description": "Last N Wrath journal events. Optional kind and session_id filters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "default": 15},
                "kind": {"type": "string"},
                "session_id": {"type": "string"},
            },
        },
    },
    {
        "name": "wrath_last_deny",
        "description": "Last N Wrath/harness denials with rule_id and reason.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "default": 8},
                "session_id": {"type": "string"},
            },
        },
    },
    {
        "name": "wrath_doctor",
        "description": "Check Wrath paths, MCP, hooks, config, policy smoke.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "wrath_config",
        "description": "Effective Wrath settings.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "wrath_budget_tips",
        "description": "Budget tips plus journal tool/event counts.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "wrath_set_enabled",
        "description": "Enable or disable Wrath runtime. args: enabled bool.",
        "inputSchema": {
            "type": "object",
            "properties": {"enabled": {"type": "boolean"}},
            "required": ["enabled"],
        },
    },
    {
        "name": "wrath_set_orchestrate",
        "description": "Enable or disable style-dispatch orchestration (mode= over model=).",
        "inputSchema": {
            "type": "object",
            "properties": {"orchestrate": {"type": "boolean"}},
            "required": ["orchestrate"],
        },
    },
    {
        "name": "wrath_set_privacy",
        "description": "Enable or disable privacy mode (bulk upload deny).",
        "inputSchema": {
            "type": "object",
            "properties": {"privacy": {"type": "boolean"}},
            "required": ["privacy"],
        },
    },
    {
        "name": "wrath_set_yolo",
        "description": "Enable or disable YOLO soft-guard profile (allows force-push/reset/pipe).",
        "inputSchema": {
            "type": "object",
            "properties": {"yolo": {"type": "boolean"}},
            "required": ["yolo"],
        },
    },
    {
        "name": "wrath_set_profile",
        "description": "Set profile: default|thin|strict|privacy|fleet|max|yolo.",
        "inputSchema": {
            "type": "object",
            "properties": {"profile": {"type": "string"}},
            "required": ["profile"],
        },
    },
    {
        "name": "wrath_policy_check",
        "description": "Dry-run policy against tool + command and/or tool_input JSON.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "tool": {"type": "string", "default": "run_terminal_command"},
                "tool_input": {"type": "object"},
            },
        },
    },
    {
        "name": "wrath_session_stats",
        "description": "Per-session tool histogram and recent denies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "top_tools": {"type": "integer", "default": 8},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "wrath_session_report",
        "description": "Compact session summary for ship/check.",
        "inputSchema": {
            "type": "object",
            "properties": {"session_id": {"type": "string"}},
            "required": ["session_id"],
        },
    },
]


def handle_tool(name: str, args: dict) -> str:
    d = data_dir()
    cfg = load_project_config(discover_start())
    version = plugin_version()

    if name == "wrath_status":
        return json.dumps(
            {
                "version": version,
                "enabled": is_wrath_enabled(d),
                "profile": get_profile(d, project=cfg),
                "strict": is_strict(d, project=cfg),
                "orchestrate": is_orchestrate(d),
                "privacy": is_privacy(d),
                "yolo": is_yolo(d, project=cfg),
                "budget_tools": budget_tools_effective(cfg),
                "reread_warn": reread_warn_effective(cfg),
                "privacy_upload": cfg.privacy_upload,
                "require_spawn_model": cfg.require_spawn_model,
                "project_config": str(cfg.path) if cfg.path else None,
                "counts": counts(d),
            },
            indent=2,
        )

    if name == "wrath_journal_tail":
        n = int(args.get("n") or 15)
        kind = args.get("kind")
        sid = args.get("session_id")
        rows = tail(
            d,
            n=n,
            kind=str(kind) if kind else None,
            session_id=str(sid) if sid else None,
        )
        return json.dumps(
            {"enabled": is_wrath_enabled(d), "path": str(journal_path(d)), "events": rows},
            indent=2,
        )

    if name == "wrath_last_deny":
        n = int(args.get("n") or 8)
        sid = args.get("session_id")
        rows = last_denies(d, n=n, session_id=str(sid) if sid else None)
        return json.dumps({"denies": rows, "count": len(rows)}, indent=2)

    if name == "wrath_set_enabled":
        return json.dumps(
            set_wrath_enabled(bool(args.get("enabled")), data_dir=d, source="mcp"),
            indent=2,
        )
    if name == "wrath_set_orchestrate":
        return json.dumps(
            set_orchestrate(bool(args.get("orchestrate")), data_dir=d, source="mcp"),
            indent=2,
        )
    if name == "wrath_set_privacy":
        return json.dumps(
            set_privacy(bool(args.get("privacy")), data_dir=d, source="mcp"),
            indent=2,
        )
    if name == "wrath_set_yolo":
        return json.dumps(set_yolo(bool(args.get("yolo")), data_dir=d, source="mcp"), indent=2)
    if name == "wrath_set_profile":
        return json.dumps(
            set_profile(str(args.get("profile") or "default"), data_dir=d, source="mcp"),
            indent=2,
        )

    if name == "wrath_config":
        return json.dumps(
            {
                "version": version,
                "enabled": is_wrath_enabled(d),
                "profile": get_profile(d, project=cfg),
                "strict": is_strict(d, project=cfg),
                "orchestrate": is_orchestrate(d),
                "privacy": is_privacy(d),
                "yolo": is_yolo(d, project=cfg),
                "budget_tools": budget_tools_effective(cfg),
                "reread_warn": reread_warn_effective(cfg),
                "nested_shell_depth": cfg.nested_shell_depth,
                "privacy_upload": cfg.privacy_upload,
                "require_spawn_model": cfg.require_spawn_model,
                "project_config": str(cfg.path) if cfg.path else None,
                "project_deny_count": len(cfg.deny),
                "config_version": cfg.version,
                "state": load_state(d),
                "data_dir": str(d),
            },
            indent=2,
        )

    if name == "wrath_doctor":
        root = Path(os.environ.get("GROK_PLUGIN_ROOT") or Path(__file__).resolve().parents[3])
        hooks = root / "hooks" / "hooks.json"
        pre = root / "hooks" / "pre_tool_use.py"
        src_ok = (root / "src" / "wrath" / "policy" / "engine.py").is_file()
        deny = evaluate(
            "run_terminal_command",
            "rm -rf /",
            config=cfg,
            strict=is_strict(d, project=cfg),
        )
        allow = evaluate(
            "run_terminal_command",
            "git status",
            config=cfg,
            strict=is_strict(d, project=cfg),
        )
        nested = evaluate(
            "run_terminal_command",
            "powershell -Command \"bash -c 'rm -rf /'\"",
            config=cfg,
        )
        mcp = _mcp_health(root)
        hook_events = []
        if hooks.is_file():
            try:
                hj = json.loads(hooks.read_text(encoding="utf-8"))
                hook_events = list((hj.get("hooks") or {}).keys())
            except (OSError, json.JSONDecodeError):
                pass
        return json.dumps(
            {
                "plugin_root": str(root),
                "data_dir": str(d),
                "version": version,
                "src_package": src_ok,
                "enabled": is_wrath_enabled(d),
                "profile": get_profile(d, project=cfg),
                "strict": is_strict(d, project=cfg),
                "orchestrate": is_orchestrate(d),
                "privacy": is_privacy(d),
                "yolo": is_yolo(d, project=cfg),
                "state": load_state(d),
                "project_config": str(cfg.path) if cfg.path else None,
                "hooks_json": hooks.is_file(),
                "hook_events": hook_events,
                "pre_tool_use": pre.is_file(),
                **mcp,
                "journal_exists": journal_path(d).is_file(),
                "counts": counts(d),
                "policy_smoke": {
                    "deny_rm_root": (not deny.allow),
                    "allow_git_status": allow.allow,
                    "deny_nested_shell": (not nested.allow),
                },
                "python": sys.version.split()[0],
            },
            indent=2,
        )

    if name == "wrath_budget_tips":
        c = counts(d)
        tips = [
            "Grep before full-file reads; avoid re-read loops.",
            "Prefer small edits over rewriting large files.",
            "Use /wrath-thin for one-file fixes; /wrath-check before claiming done.",
            "Subagents only for independent parallel work; pin model= when orch on.",
            "Call wrath_session_stats / wrath_session_report after long turns.",
        ]
        return json.dumps({"counts": c, "tips": tips, "version": version}, indent=2)

    if name == "wrath_policy_check":
        cmd = str(args.get("command") or "")
        tool = str(args.get("tool") or "run_terminal_command")
        ti = args.get("tool_input") if isinstance(args.get("tool_input"), dict) else {}
        dec = evaluate(
            tool,
            cmd,
            ti,
            config=cfg,
            strict=is_strict(d, project=cfg),
            orchestrate=is_orchestrate(d),
            privacy=is_privacy(d),
            yolo=is_yolo(d, project=cfg),
        )
        return json.dumps(
            {
                "tool": tool,
                "command": cmd,
                "tool_input": ti,
                "allow": dec.allow,
                "reason": dec.reason,
                "warning": dec.warning,
                "rule_id": dec.rule_id,
                "enabled": is_wrath_enabled(d),
                "strict": is_strict(d, project=cfg),
                "privacy": is_privacy(d),
                "yolo": is_yolo(d, project=cfg),
                "orchestrate": is_orchestrate(d),
            },
            indent=2,
        )

    if name == "wrath_session_stats":
        sid = str(args.get("session_id") or "")
        top = int(args.get("top_tools") or 8)
        if not sid:
            return json.dumps({"error": "session_id required"})
        return json.dumps(session_stats(d, sid, top_tools=top), indent=2)

    if name == "wrath_session_report":
        sid = str(args.get("session_id") or "")
        if not sid:
            return json.dumps({"error": "session_id required"})
        stats = session_stats(d, sid)
        c = counts(d, session_id=sid)
        return json.dumps(
            {
                "session_id": sid,
                "version": version,
                "counts": c,
                "tool_histogram": stats.get("tool_histogram"),
                "deny_count": stats.get("deny_count"),
                "recent_denies": stats.get("denies"),
                "profile": get_profile(d, project=cfg),
                "modes": {
                    "strict": is_strict(d, project=cfg),
                    "orchestrate": is_orchestrate(d),
                    "privacy": is_privacy(d),
                    "yolo": is_yolo(d, project=cfg),
                },
            },
            indent=2,
        )

    return json.dumps({"error": f"unknown tool {name}"})
