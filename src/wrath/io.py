"""Paths, stdin/stdout, MCP heal, secret path heuristics (stdlib only)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def plugin_root() -> Path:
    raw = os.environ.get("GROK_PLUGIN_ROOT") or os.environ.get("CLAUDE_PLUGIN_ROOT")
    if raw:
        return Path(raw)
    # src/wrath/io.py → package root is parents[2]
    return Path(__file__).resolve().parents[2]


def plugin_data() -> Path:
    raw = os.environ.get("GROK_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if raw:
        path = Path(raw)
    else:
        path = Path.home() / ".wrath-addon" / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def plugin_version() -> str:
    from wrath.version import plugin_version as _pv

    return _pv()


def mcp_launcher_path(root: Path | None = None) -> Path:
    base = root or plugin_root()
    if sys.platform == "win32":
        launcher = base / "mcp" / "launch.cmd"
        if launcher.is_file():
            return launcher
    else:
        launcher = base / "mcp" / "launch.sh"
        if launcher.is_file():
            return launcher
    return base / "mcp" / "run.py"


def ensure_mcp_config(root: Path | None = None) -> bool:
    """Patch installed .mcp.json to an absolute launcher path."""
    base = root or plugin_root()
    mcp_json = base / ".mcp.json"
    launcher = mcp_launcher_path(base)
    if not launcher.is_file():
        return False
    abs_launcher = str(launcher.resolve())
    desired = {
        "mcpServers": {
            "wrath": {
                "command": abs_launcher,
                "args": [],
            }
        }
    }
    try:
        current: dict[str, Any] = {}
        if mcp_json.is_file():
            loaded = json.loads(mcp_json.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                current = loaded
        if current == desired:
            return True
        mcp_json.write_text(json.dumps(desired, indent=2) + "\n", encoding="utf-8")
        return True
    except (OSError, TypeError, ValueError):
        return False


def read_stdin_json() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def emit(obj: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))
    sys.stdout.flush()


def log_hook_error(hook: str, exc: BaseException, data_dir: Path | None = None) -> None:
    msg = f"Wrath {hook}: {type(exc).__name__}: {exc}"
    try:
        print(msg, file=sys.stderr)
    except Exception:
        pass
    try:
        d = data_dir or plugin_data()
        d.mkdir(parents=True, exist_ok=True)
        path = d / "hook_errors.jsonl"
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "hook": hook,
            "error": f"{type(exc).__name__}: {exc}",
        }
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass


def split_shell_segments(cmd: str) -> list[str]:
    """Split on `;`, `&&`, `||` only — bare `|` kept for pipe-exec gates."""
    if not cmd or not cmd.strip():
        return []
    parts: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    i = 0
    s = cmd
    while i < len(s):
        ch = s[i]
        if quote:
            buf.append(ch)
            if ch == quote and (i == 0 or s[i - 1] != "\\"):
                quote = None
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if (
            ch == ";"
            or (ch == "&" and i + 1 < len(s) and s[i + 1] == "&")
            or (ch == "|" and i + 1 < len(s) and s[i + 1] == "|")
        ):
            seg = "".join(buf).strip()
            if seg:
                parts.append(seg)
            buf = []
            i += 2 if ch in ("&", "|") else 1
            continue
        buf.append(ch)
        i += 1
    seg = "".join(buf).strip()
    if seg:
        parts.append(seg)
    return parts or [cmd.strip()]


def normalize_path_key(path: str) -> str:
    p = (path or "").replace("\\", "/").strip()
    while "//" in p:
        p = p.replace("//", "/")
    return p.rstrip("/").lower()


def looks_like_secret_path(path: str) -> bool:
    p = (path or "").replace("\\", "/").rstrip("/")
    if not p:
        return False
    base = p.split("/")[-1]
    if not base:
        return False
    low = base.lower()

    if low == ".env" or low.startswith(".env."):
        return True
    if low in {
        "id_rsa",
        "id_ed25519",
        "id_ecdsa",
        "id_dsa",
        "credentials.json",
        "aws_credentials",
        ".npmrc",
        ".pypirc",
        ".netrc",
    }:
        return True
    norm = low.replace("-", "_")
    if "service_account" in norm and low.endswith(".json"):
        return True
    if low.endswith("_sa.json") or low.endswith("-sa.json"):
        return True
    if "/.ssh/" in f"/{p.lower()}" and not low.endswith(".pub"):
        if low.startswith("id_"):
            return True
        if "private" in low or low.endswith(".pem"):
            return True
    if low.endswith(".pem") and any(x in low for x in ("key", "private", "cert", "id_")):
        return True
    return False
