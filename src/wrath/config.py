"""Project config .wrath.toml / .wrath.json — schema v1 + v2."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

DEFAULT_BUDGET_TOOLS = 80
DEFAULT_REREAD_WARN = 3
DEFAULT_NESTED_DEPTH = 3
MAX_DENY_PATTERN_LEN = 200
MAX_DENY_PATTERNS = 32
CONFIG_NAMES = (".wrath.toml", ".wrath.json")

PrivacyMode = Literal["off", "warn", "deny"]
SpawnModelMode = Literal["off", "warn", "deny"]

PROFILES = ("default", "thin", "strict", "privacy", "fleet", "max")


@dataclass(frozen=True)
class EffectiveConfig:
    """Merged project settings (file only; env overlays applied by callers)."""

    version: int = 1
    profile: str = "default"
    strict: bool = False
    budget_tools: int = DEFAULT_BUDGET_TOOLS
    reread_warn: int = DEFAULT_REREAD_WARN
    nested_shell_depth: int = DEFAULT_NESTED_DEPTH
    deny: tuple[str, ...] = field(default_factory=tuple)
    privacy_upload: PrivacyMode = "warn"
    require_spawn_model: SpawnModelMode = "off"
    path: Path | None = None


def _defaults() -> EffectiveConfig:
    return EffectiveConfig()


def discover_start(event: dict[str, Any] | None = None) -> Path:
    if event:
        for key in ("cwd", "workingDirectory", "working_directory", "workspaceRoot"):
            raw = event.get(key)
            if raw:
                p = Path(str(raw))
                if p.is_dir():
                    return p
    for env_key in ("GROK_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "GROK_WORKSPACE_ROOT", "PWD"):
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
    try:
        import tomllib
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


def _clamp_mode(val: Any, default: str) -> str:
    s = str(val or default).strip().lower()
    if s in ("off", "warn", "deny"):
        return s
    return default


def _profile_defaults(name: str) -> dict[str, Any]:
    n = (name or "default").strip().lower()
    if n not in PROFILES:
        n = "default"
    base: dict[str, Any] = {
        "privacy_upload": "warn",
        "require_spawn_model": "off",
        "strict": False,
        "orchestrate": False,
        "il": False,
        "privacy": False,
    }
    if n == "thin":
        base["privacy_upload"] = "off"
    elif n == "strict":
        base["strict"] = True
        base["privacy_upload"] = "warn"
        base["require_spawn_model"] = "warn"
    elif n == "privacy":
        base["privacy"] = True
        base["privacy_upload"] = "deny"
        base["strict"] = True
    elif n == "fleet":
        base["orchestrate"] = True
        base["il"] = True
        base["require_spawn_model"] = "warn"
    elif n == "max":
        base["strict"] = True
        base["orchestrate"] = True
        base["il"] = True
        base["privacy"] = True
        base["privacy_upload"] = "deny"
        base["require_spawn_model"] = "deny"
    return base


def load_project_config(start: Path | None = None) -> EffectiveConfig:
    path = find_config_file(start)
    if not path:
        return _defaults()
    try:
        data = _parse_file(path)
    except (OSError, json.JSONDecodeError, ValueError):
        return EffectiveConfig(path=path)

    version = 1
    try:
        version = int(data.get("version") or 1)
    except (TypeError, ValueError):
        version = 1

    profile = str(data.get("profile") or "default").strip().lower()
    if profile not in PROFILES:
        profile = "default"
    pdata = _profile_defaults(profile)

    # Nested tables (v2)
    policy = data.get("policy") if isinstance(data.get("policy"), dict) else {}
    modes = data.get("modes") if isinstance(data.get("modes"), dict) else {}
    profiles = data.get("profiles") if isinstance(data.get("profiles"), dict) else {}
    prof_override = profiles.get(profile) if isinstance(profiles.get(profile), dict) else {}

    def pick(*keys: str, default: Any = None) -> Any:
        for src in (prof_override, policy, modes, data):
            if not isinstance(src, dict):
                continue
            for k in keys:
                if k in src and src[k] is not None:
                    return src[k]
        return default

    budget = pick("budget_tools", default=DEFAULT_BUDGET_TOOLS)
    try:
        budget_i = max(int(budget), 1)
    except (TypeError, ValueError):
        budget_i = DEFAULT_BUDGET_TOOLS

    reread = pick("reread_warn", default=DEFAULT_REREAD_WARN)
    try:
        reread_i = max(int(reread), 0)
    except (TypeError, ValueError):
        reread_i = DEFAULT_REREAD_WARN

    depth = pick("nested_shell_depth", default=DEFAULT_NESTED_DEPTH)
    try:
        depth_i = max(min(int(depth), 8), 1)
    except (TypeError, ValueError):
        depth_i = DEFAULT_NESTED_DEPTH

    privacy_upload = _clamp_mode(
        pick("privacy_upload", default=pdata["privacy_upload"]),
        pdata["privacy_upload"],
    )
    require_spawn = _clamp_mode(
        pick("require_spawn_model", default=pdata["require_spawn_model"]),
        pdata["require_spawn_model"],
    )

    strict = bool(pick("strict", default=pdata["strict"] or data.get("strict", False)))
    deny = _sanitize_denies(pick("deny", default=data.get("deny")))

    return EffectiveConfig(
        version=version,
        profile=profile,
        strict=strict,
        budget_tools=budget_i,
        reread_warn=reread_i,
        nested_shell_depth=depth_i,
        deny=deny,
        privacy_upload=privacy_upload,  # type: ignore[arg-type]
        require_spawn_model=require_spawn,  # type: ignore[arg-type]
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


def nested_depth_effective(cfg: EffectiveConfig | None = None) -> int:
    raw = os.environ.get("WRATH_NESTED_DEPTH", "").strip()
    if raw.isdigit():
        return max(min(int(raw), 8), 1)
    return (cfg or _defaults()).nested_shell_depth
