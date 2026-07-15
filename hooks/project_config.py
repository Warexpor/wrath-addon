"""Project-local Wrath config (.wrath.toml / .wrath.json). Stdlib only."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_BUDGET_TOOLS = 80
DEFAULT_REREAD_WARN = 3
MAX_DENY_PATTERN_LEN = 200
MAX_DENY_PATTERNS = 32
CONFIG_NAMES = (".wrath.toml", ".wrath.json")


@dataclass(frozen=True)
class EffectiveConfig:
    """Project-file settings only (env overlays applied by callers)."""

    strict: bool = False
    budget_tools: int = DEFAULT_BUDGET_TOOLS
    reread_warn: int = DEFAULT_REREAD_WARN
    deny: tuple[str, ...] = field(default_factory=tuple)
    path: Path | None = None


def _defaults() -> EffectiveConfig:
    return EffectiveConfig()


def discover_start(event: dict[str, Any] | None = None) -> Path:
    """Best-effort project root walk start."""
    if event:
        for key in ("cwd", "workingDirectory", "working_directory", "workspaceRoot"):
            raw = event.get(key)
            if raw:
                p = Path(str(raw))
                if p.is_dir():
                    return p
    for env_key in ("GROK_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "PWD"):
        raw = os.environ.get(env_key)
        if raw:
            p = Path(raw)
            if p.is_dir():
                return p
    return Path.cwd()


def find_config_file(start: Path | None = None) -> Path | None:
    cur = (start or Path.cwd()).resolve()
    if cur.is_file():
        cur = cur.parent
    for _ in range(24):
        for name in CONFIG_NAMES:
            candidate = cur / name
            if candidate.is_file():
                return candidate
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return None


def _parse_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    # TOML
    try:
        import tomllib  # py311+
    except ImportError:
        return {}
    data = tomllib.loads(text)
    return data if isinstance(data, dict) else {}


def _sanitize_denies(raw: Any) -> tuple[str, ...]:
    if not isinstance(raw, list):
        return ()
    out: list[str] = []
    for item in raw[:MAX_DENY_PATTERNS]:
        s = str(item).strip()
        if not s or len(s) > MAX_DENY_PATTERN_LEN:
            continue
        try:
            re.compile(s)
        except re.error:
            continue
        out.append(s)
    return tuple(out)


def load_project_config(start: Path | None = None) -> EffectiveConfig:
    path = find_config_file(start)
    if not path:
        return _defaults()
    try:
        data = _parse_file(path)
    except (OSError, json.JSONDecodeError, ValueError):
        return EffectiveConfig(path=path)

    budget = data.get("budget_tools", DEFAULT_BUDGET_TOOLS)
    try:
        budget_i = max(int(budget), 1)
    except (TypeError, ValueError):
        budget_i = DEFAULT_BUDGET_TOOLS

    reread = data.get("reread_warn", DEFAULT_REREAD_WARN)
    try:
        reread_i = max(int(reread), 0)
    except (TypeError, ValueError):
        reread_i = DEFAULT_REREAD_WARN

    return EffectiveConfig(
        strict=bool(data.get("strict", False)),
        budget_tools=budget_i,
        reread_warn=reread_i,
        deny=_sanitize_denies(data.get("deny")),
        path=path,
    )


def budget_tools_effective(cfg: EffectiveConfig | None = None) -> int:
    raw = os.environ.get("WRATH_BUDGET_TOOLS", "").strip()
    if raw.isdigit():
        return max(int(raw), 1)
    return (cfg or _defaults()).budget_tools


def reread_warn_effective(cfg: EffectiveConfig | None = None) -> int:
    raw = os.environ.get("WRATH_REREAD_WARN", "").strip()
    if raw.isdigit():
        return max(int(raw), 0)
    return (cfg or _defaults()).reread_warn
