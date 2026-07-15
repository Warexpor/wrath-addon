"""Drive pack + status line."""

from __future__ import annotations

from pathlib import Path

from wrath.io import plugin_version
from wrath.modes.il import IL_BODY
from wrath.modes.orchestrate import ORCHESTRATE_BODY
from wrath.modes.privacy import PRIVACY_BODY
from wrath.modes.yolo import YOLO_BODY

DRIVE_BODY = """Drive: cold, brief, ship. Key point first. No filler.
Ladder: need → reuse → stdlib → one line → min code. Delete > add.
Verify before done. Grep before re-read. /wrath-thin · /wrath-check · /wrath-ship
Safety: footgun guards on. Profiles: /wrath-profile · privacy · yolo
Strict: /wrath-strict · fleet: /wrath-orchestrate · IL: /wrath-il · YOLO: /wrath-yolo
MCP: wrath_status · wrath_doctor · wrath_policy_check · wrath_last_deny · wrath_journal_tail
"""


def status_line(
    *,
    enabled: bool,
    strict: bool,
    budget: int,
    config_path: Path | None = None,
    version: str | None = None,
    orchestrate: bool = False,
    il: bool = False,
    privacy: bool = False,
    yolo: bool = False,
    profile: str = "default",
) -> str:
    ver = version or plugin_version()
    on = "ON" if enabled else "OFF"
    st = "on" if strict else "off"
    orch = "on" if orchestrate else "off"
    il_s = "on" if il else "off"
    priv = "on" if privacy else "off"
    yo = "on" if yolo else "off"
    cfg = config_path.name if config_path else "none"
    return (
        f"[Wrath v{ver} · {on} · profile={profile} · strict={st} · orch={orch} · "
        f"il={il_s} · privacy={priv} · yolo={yo} · budget={budget} · config={cfg}]"
    )


def drive_system_message(
    *,
    enabled: bool = True,
    strict: bool = False,
    budget: int = 80,
    config_path: Path | None = None,
    orchestrate: bool = False,
    il: bool = False,
    privacy: bool = False,
    yolo: bool = False,
    profile: str = "default",
) -> str:
    line = status_line(
        enabled=enabled,
        strict=strict,
        budget=budget,
        config_path=config_path,
        orchestrate=orchestrate,
        il=il,
        privacy=privacy,
        yolo=yolo,
        profile=profile,
    )
    if not enabled:
        return (
            f"{line}\n"
            "Guards, drive pack, and prompt nudges are disabled. "
            "/wrath-on or “turn wrath on” to re-enable."
        )
    body = DRIVE_BODY.strip()
    if orchestrate:
        body = f"{body}\n{ORCHESTRATE_BODY.strip()}"
    if il:
        body = f"{body}\n{IL_BODY.strip()}"
    if privacy:
        body = f"{body}\n{PRIVACY_BODY.strip()}"
    if yolo:
        body = f"{body}\n{YOLO_BODY.strip()}"
    return f"{line}\n{body}"
