from __future__ import annotations

import re

from wrath.policy.decision import Decision

PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(
            r"\brm\s+(?:-[a-zA-Z]+\s+)*(?:--\S+\s+)*(?:/\s*$|/\*(?:\s|$)|~\s*$|~/\*|/home\s*$|/Users\s*$)",
            re.I,
        ),
        "destructive_fs",
        "Wrath: blocked destructive rm targeting filesystem root/home",
    ),
    (
        re.compile(
            r"remove-item\s+.+(?:-recurse|-force).+(?:-recurse|-force).+[cC]:\\\s*$",
            re.I,
        ),
        "destructive_fs",
        "Wrath: blocked Remove-Item -Recurse -Force on drive root",
    ),
    (
        re.compile(
            r"remove-item\s+.+(?:-recurse|-force).+(?:-recurse|-force).+(?:\$home|~)\\?\s*$",
            re.I,
        ),
        "destructive_fs",
        "Wrath: blocked Remove-Item wipe of home directory",
    ),
    (re.compile(r"\bformat-volume\b", re.I), "destructive_fs", "Wrath: blocked Format-Volume"),
    (re.compile(r"\bmkfs(\.|$|\s)", re.I), "destructive_fs", "Wrath: blocked mkfs"),
    (
        re.compile(r":\(\)\s*\{\s*:\|:&\s*\}\s*;\s*:", re.I),
        "destructive_fs",
        "Wrath: blocked fork bomb",
    ),
    (
        re.compile(r">\s*/dev/sd[a-z]", re.I),
        "destructive_fs",
        "Wrath: blocked write to raw block device",
    ),
    (
        re.compile(r"\bdd\s+.*\bof=/dev/", re.I),
        "destructive_fs",
        "Wrath: blocked dd to /dev/*",
    ),
    (
        re.compile(r"\bformat\s+[a-zA-Z]:\s*$", re.I),
        "destructive_fs",
        "Wrath: blocked format on drive letter",
    ),
    (
        re.compile(r"\brd\s+/s\s+/q\s+[a-zA-Z]:\\?\s*$", re.I),
        "destructive_fs",
        "Wrath: blocked rd /s /q on drive root",
    ),
    (
        re.compile(r"\bdel\s+(?:/[a-zA-Z]+\s+)+[a-zA-Z]:\\?\s*$", re.I),
        "destructive_fs",
        "Wrath: blocked del /s on drive root",
    ),
    (
        re.compile(r"\b(shutdown|reboot|poweroff)\b.*\b(-h\s+now|/s\s|/r\s)", re.I),
        "destructive_fs",
        "Wrath: blocked system shutdown/reboot",
    ),
    (
        re.compile(r"\bcipher\s+/w:", re.I),
        "destructive_fs",
        "Wrath: blocked cipher /w (secure wipe)",
    ),
    (
        re.compile(r"\bsudo\s+rm\s+-[a-zA-Z]*r[a-zA-Z]*f\s+/", re.I),
        "destructive_fs",
        "Wrath: blocked sudo rm -rf /",
    ),
]


def check_destructive(cmd: str) -> Decision | None:
    compact = " ".join(cmd.split())
    for pat, rid, reason in PATTERNS:
        if pat.search(compact):
            return Decision(allow=False, reason=reason, rule_id=rid, severity="deny")
    low = compact.lower()
    if re.search(r"remove-item\s+.*-recurse\s+.*-force", low) or re.search(
        r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f", low
    ):
        return Decision(
            allow=True,
            warning="Wrath: recursive force delete — double-check path.",
            rule_id="destructive_fs_warn",
            severity="warn",
        )
    if re.search(r"\bchmod\s+777\b", low):
        return Decision(
            allow=True,
            warning="Wrath: chmod 777 is usually wrong — prefer tighter perms.",
            rule_id="chmod_777",
            severity="warn",
        )
    return None
