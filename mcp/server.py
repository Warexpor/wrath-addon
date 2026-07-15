#!/usr/bin/env python3
"""Stdio MCP server for Wrath addon (stdlib only)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "hooks"))

from common import plugin_version  # noqa: E402
from journal import counts, journal_path, session_stats, tail  # noqa: E402
from policy import evaluate  # noqa: E402
from project_config import (  # noqa: E402
    budget_tools_effective,
    discover_start,
    load_project_config,
    reread_warn_effective,
)
from toggle import (  # noqa: E402
    is_strict,
    is_wrath_enabled,
    load_state,
    set_wrath_enabled,
)

VERSION = plugin_version()


def data_dir() -> Path:
    raw = os.environ.get("GROK_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if raw:
        p = Path(raw)
    else:
        p = Path.home() / ".wrath-addon" / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _mcp_health(root: Path) -> dict:
    mcp_json = root / ".mcp.json"
    run_py = root / "mcp" / "run.py"
    absolute = False
    args: list = []
    exists = run_py.is_file()
    fix = None
    if mcp_json.is_file():
        try:
            cfg = json.loads(mcp_json.read_text(encoding="utf-8"))
            servers = cfg.get("mcpServers") or cfg.get("mcp_servers") or {}
            wrath = servers.get("wrath") or {}
            args = list(wrath.get("args") or [])
            if args:
                candidate = Path(str(args[0]))
                absolute = candidate.is_absolute()
                if absolute:
                    exists = candidate.is_file()
                else:
                    exists = (
                        (root / candidate).is_file()
                        if not candidate.is_absolute()
                        else candidate.is_file()
                    )
        except (OSError, json.JSONDecodeError, TypeError):
            fix = r".\install.ps1  # re-patch absolute MCP path"
    if not absolute or not exists:
        fix = r".\install.ps1  # re-patch absolute MCP path"
    return {
        "mcp_json": mcp_json.is_file(),
        "mcp_args": args,
        "mcp_args_absolute": absolute,
        "mcp_run_exists": exists,
        "fix": fix,
    }


TOOLS = [
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
        "name": "wrath_doctor",
        "description": "Check Wrath paths, MCP absolute path, config, policy smoke.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "wrath_config",
        "description": "Effective Wrath settings (enabled, strict, budget, reread, config).",
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
        "name": "wrath_policy_check",
        "description": "Dry-run Wrath PreToolUse policy against a shell command.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "tool": {"type": "string", "default": "run_terminal_command"},
            },
            "required": ["command"],
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
]


def handle_tool(name: str, args: dict) -> str:
    d = data_dir()
    cfg = load_project_config(discover_start())
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
            {
                "enabled": is_wrath_enabled(d),
                "path": str(journal_path(d)),
                "events": rows,
            },
            indent=2,
        )
    if name == "wrath_set_enabled":
        en = bool(args.get("enabled"))
        state = set_wrath_enabled(en, data_dir=d, source="mcp")
        return json.dumps(state, indent=2)
    if name == "wrath_config":
        return json.dumps(
            {
                "version": VERSION,
                "enabled": is_wrath_enabled(d),
                "strict": is_strict(d, project=cfg),
                "budget_tools": budget_tools_effective(cfg),
                "reread_warn": reread_warn_effective(cfg),
                "project_config": str(cfg.path) if cfg.path else None,
                "project_deny_count": len(cfg.deny),
                "state": load_state(d),
                "data_dir": str(d),
            },
            indent=2,
        )
    if name == "wrath_doctor":
        root = Path(os.environ.get("GROK_PLUGIN_ROOT") or str(ROOT))
        hooks = root / "hooks" / "hooks.json"
        pre = root / "hooks" / "pre_tool_use.py"
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
        mcp = _mcp_health(root)
        report = {
            "plugin_root": str(root),
            "data_dir": str(d),
            "enabled": is_wrath_enabled(d),
            "strict": is_strict(d, project=cfg),
            "state": load_state(d),
            "project_config": str(cfg.path) if cfg.path else None,
            "budget_tools": budget_tools_effective(cfg),
            "reread_warn": reread_warn_effective(cfg),
            "hooks_json": hooks.is_file(),
            "pre_tool_use": pre.is_file(),
            **mcp,
            "journal_exists": journal_path(d).is_file(),
            "counts": counts(d),
            "policy_smoke": {
                "deny_rm_root": (not deny.allow),
                "allow_git_status": allow.allow,
            },
            "python": sys.version.split()[0],
            "version": VERSION,
        }
        return json.dumps(report, indent=2)
    if name == "wrath_budget_tips":
        c = counts(d)
        tips = [
            "Grep before full-file reads; avoid re-read loops.",
            "Prefer small edits over rewriting large files.",
            "Use /wrath-thin for one-file fixes; /wrath-check before claiming done.",
            "Subagents only for independent parallel work.",
            "Call wrath_session_stats with the current session_id after long turns.",
        ]
        return json.dumps({"counts": c, "tips": tips, "version": VERSION}, indent=2)
    if name == "wrath_policy_check":
        cmd = str(args.get("command") or "")
        tool = str(args.get("tool") or "run_terminal_command")
        dec = evaluate(tool, cmd, {}, config=cfg, strict=is_strict(d, project=cfg))
        return json.dumps(
            {
                "tool": tool,
                "command": cmd,
                "allow": dec.allow,
                "reason": dec.reason,
                "warning": dec.warning,
                "enabled": is_wrath_enabled(d),
                "strict": is_strict(d, project=cfg),
            },
            indent=2,
        )
    if name == "wrath_session_stats":
        sid = str(args.get("session_id") or "")
        top = int(args.get("top_tools") or 8)
        if not sid:
            return json.dumps({"error": "session_id required"})
        return json.dumps(session_stats(d, sid, top_tools=top), indent=2)
    return json.dumps({"error": f"unknown tool {name}"})


def respond(msg_id, result=None, error=None):
    body = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        body["error"] = error
    else:
        body["result"] = result
    sys.stdout.write(json.dumps(body) + "\n")
    sys.stdout.flush()


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = req.get("method")
        msg_id = req.get("id")
        params = req.get("params") or {}

        if method == "initialize":
            respond(
                msg_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "wrath-mcp", "version": VERSION},
                },
            )
        elif method == "notifications/initialized":
            continue
        elif method == "notifications/cancelled":
            continue
        elif method == "tools/list":
            respond(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            tname = params.get("name")
            targs = params.get("arguments") or {}
            try:
                text = handle_tool(str(tname), targs if isinstance(targs, dict) else {})
                is_err = False
                try:
                    parsed = json.loads(text)
                    is_err = isinstance(parsed, dict) and "error" in parsed
                except json.JSONDecodeError:
                    pass
                respond(
                    msg_id,
                    {
                        "content": [{"type": "text", "text": text}],
                        "isError": bool(is_err),
                    },
                )
            except Exception as exc:  # noqa: BLE001
                respond(
                    msg_id,
                    {
                        "content": [{"type": "text", "text": json.dumps({"error": str(exc)})}],
                        "isError": True,
                    },
                )
        elif method == "ping":
            respond(msg_id, {})
        elif method == "resources/list":
            respond(msg_id, {"resources": []})
        elif method == "prompts/list":
            respond(msg_id, {"prompts": []})
        elif msg_id is not None:
            respond(msg_id, error={"code": -32601, "message": f"Method not found: {method}"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
