"""Compact Wrath drive pack + status line for SessionStart."""

from __future__ import annotations

from pathlib import Path

from common import plugin_version

DRIVE_BODY = """Drive: cold, brief, ship. Key point first. No filler.
Ladder: need → reuse → stdlib → one line → min code. Delete > add.
Verify before done. Grep before re-read. /wrath-thin · /wrath-check · /wrath-ship
Safety: footgun guards on (force-push main, reset --hard, root wipe, curl|sh, …).
Strict: /wrath-strict or WRATH_STRICT=1. Config: .wrath.toml / .wrath.json
MCP: wrath_doctor · wrath_config · wrath_policy_check · wrath_journal_tail
"""


def status_line(
    *,
    enabled: bool,
    strict: bool,
    budget: int,
    config_path: Path | None = None,
    version: str | None = None,
) -> str:
    ver = version or plugin_version()
    on = "ON" if enabled else "OFF"
    st = "on" if strict else "off"
    cfg = config_path.name if config_path else "none"
    return f"[Wrath v{ver} · {on} · strict={st} · budget={budget} · config={cfg}]"


def drive_system_message(
    *,
    enabled: bool = True,
    strict: bool = False,
    budget: int = 80,
    config_path: Path | None = None,
) -> str:
    line = status_line(enabled=enabled, strict=strict, budget=budget, config_path=config_path)
    if not enabled:
        return (
            f"{line}\n"
            "Guards, drive pack, and prompt nudges are disabled. "
            "/wrath-on or “turn wrath on” to re-enable."
        )
    return f"{line}\n{DRIVE_BODY.strip()}"
