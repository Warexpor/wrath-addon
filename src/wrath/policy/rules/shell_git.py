from __future__ import annotations

import os
import re

from wrath.policy.decision import Decision

FORCE_ENV = "WRATH_ALLOW_FORCE"
HARD_ENV = "WRATH_ALLOW_HARD"
CLEAN_ENV = "WRATH_ALLOW_CLEAN"


def _env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def check_git(cmd: str, *, strict: bool = False) -> Decision | None:
    low = " ".join(cmd.split()).lower()

    if re.search(r"\bgit\s+push\b", low) and re.search(r"--force|--force-with-lease|-f\b", low):
        if re.search(r"\b(main|master)\b", low) and not _env(FORCE_ENV):
            return Decision(
                allow=False,
                reason=f"Wrath: blocked force-push to main/master (set {FORCE_ENV}=1 to override)",
                rule_id="git_force_main",
                severity="deny",
            )
        if strict and not re.search(r"\b(main|master)\b", low) and not _env(FORCE_ENV):
            return Decision(
                allow=False,
                reason=(
                    f"Wrath STRICT: blocked force-push without explicit branch "
                    f"(set {FORCE_ENV}=1 or disable strict)"
                ),
                rule_id="git_force_strict",
                severity="deny",
            )
        if not _env(FORCE_ENV):
            return Decision(
                allow=True,
                warning=(
                    f"Wrath: force-push — confirm remote/branch. "
                    f"Override: {FORCE_ENV}=1 for main/master."
                ),
                rule_id="git_force_warn",
                severity="warn",
            )

    if re.search(r"\bgit\s+reset\s+--hard\b", low) and not _env(HARD_ENV):
        return Decision(
            allow=False,
            reason=f"Wrath: blocked git reset --hard (set {HARD_ENV}=1 to override)",
            rule_id="git_reset_hard",
            severity="deny",
        )

    if re.search(r"\bgit\s+clean\b", low) and re.search(r"-[a-zA-Z]*f", low):
        if re.search(r"-[a-zA-Z]*x|-[a-zA-Z]*d", low) and not _env(CLEAN_ENV):
            return Decision(
                allow=False,
                reason=f"Wrath: blocked git clean -f[dx] (set {CLEAN_ENV}=1 to override)",
                rule_id="git_clean",
                severity="deny",
            )

    if re.search(r"\bgit\s+branch\s+-[dD]\b", low) and re.search(r"\b(main|master)\b", low):
        return Decision(
            allow=False,
            reason="Wrath: blocked deleting main/master branch",
            rule_id="git_delete_main",
            severity="deny",
        )
    return None
