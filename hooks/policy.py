"""Pure deny/allow policy for PreToolUse (no I/O beyond env)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from common import looks_like_secret_path, split_shell_segments


@dataclass(frozen=True)
class Decision:
    allow: bool
    reason: str = ""
    warning: str = ""

    def as_hook_dict(self) -> dict:
        if not self.allow:
            return {"decision": "deny", "reason": self.reason or "blocked by Wrath"}
        out: dict = {"decision": "allow"}
        if self.warning:
            out["systemMessage"] = self.warning
        return out


# Shell tools (Grok + Claude + Cursor aliases)
SHELL_TOOLS = {
    "run_terminal_command",
    "Bash",
    "bash",
    "Shell",
    "shell",
    "terminal",
    "run_command",
}

FORCE_ENV = "WRATH_ALLOW_FORCE"
HARD_ENV = "WRATH_ALLOW_HARD"
CLEAN_ENV = "WRATH_ALLOW_CLEAN"
PIPE_ENV = "WRATH_ALLOW_PIPE_EXEC"
STRICT_ENV = "WRATH_STRICT"


def evaluate(tool: str, command: str = "", tool_input: dict | None = None) -> Decision:
    tool_input = tool_input or {}
    name = (tool or "").strip()
    cmd = (command or "").strip()

    if name in SHELL_TOOLS or name.lower() in {"bash", "shell", "terminal"}:
        return _eval_shell(cmd)

    path = str(
        tool_input.get("path")
        or tool_input.get("file_path")
        or tool_input.get("target_file")
        or tool_input.get("target_directory")
        or ""
    )
    if path and looks_like_secret_path(path):
        content = str(tool_input.get("content") or tool_input.get("new_string") or "")
        low_c = content.lower()
        if content and any(
            x in low_c
            for x in (
                "gist.github",
                "pastebin",
                "hastebin",
                "transfer.sh",
                "webhook.site",
            )
        ):
            return Decision(
                allow=False,
                reason="Wrath: refuse writing secrets-looking content toward public pastes",
            )
        return Decision(
            allow=True,
            warning="Wrath: sensitive path — do not print secrets to chat or remote pastes.",
        )

    # Web / HTTP tools posting likely secrets
    url = str(tool_input.get("url") or tool_input.get("uri") or "")
    body = str(tool_input.get("body") or tool_input.get("content") or "")
    if url and body and re.search(r"(api[_-]?key|secret|password|private_key)\s*[:=]", body, re.I):
        if re.search(r"pastebin|gist\.github|webhook\.site", url, re.I):
            return Decision(
                allow=False,
                reason="Wrath: blocked posting credential-like body to public paste/webhook URL",
            )

    return Decision(allow=True)


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _strict() -> bool:
    return _env_truthy(STRICT_ENV)


def _eval_shell(cmd: str) -> Decision:
    if not cmd:
        return Decision(allow=True)

    # Evaluate each segment; first deny wins; warnings accumulate lightly
    warnings: list[str] = []
    for seg in split_shell_segments(cmd):
        d = _eval_shell_segment(seg)
        if not d.allow:
            return d
        if d.warning:
            warnings.append(d.warning)
    if warnings:
        return Decision(allow=True, warning=warnings[0])
    return Decision(allow=True)


def _eval_shell_segment(cmd: str) -> Decision:
    compact = " ".join(cmd.split())
    low = compact.lower()

    deny_patterns: list[tuple[re.Pattern[str], str]] = [
        # Only root/home wipe — not e.g. rm -rf /tmp/foo
        (
            re.compile(
                r"\brm\s+(?:-[a-zA-Z]+\s+)*(?:--\S+\s+)*(?:/\s*$|/\*(?:\s|$)|~\s*$|~/\*|/home\s*$|/Users\s*$)",
                re.I,
            ),
            "Wrath: blocked destructive rm targeting filesystem root/home",
        ),
        (
            re.compile(
                r"remove-item\s+.+(?:-recurse|-force).+(?:-recurse|-force).+[cC]:\\\s*$",
                re.I,
            ),
            "Wrath: blocked Remove-Item -Recurse -Force on drive root",
        ),
        (
            re.compile(
                r"remove-item\s+.+(?:-recurse|-force).+(?:-recurse|-force).+(?:\$home|~)\\?\s*$",
                re.I,
            ),
            "Wrath: blocked Remove-Item wipe of home directory",
        ),
        (
            re.compile(r"\bformat-volume\b", re.I),
            "Wrath: blocked Format-Volume",
        ),
        (
            re.compile(r"\bmkfs(\.|$|\s)", re.I),
            "Wrath: blocked mkfs",
        ),
        (
            re.compile(r":\(\)\s*\{\s*:\|:&\s*\}\s*;\s*:", re.I),
            "Wrath: blocked fork bomb",
        ),
        (
            re.compile(r">\s*/dev/sd[a-z]", re.I),
            "Wrath: blocked write to raw block device",
        ),
        (
            re.compile(r"\bdd\s+.*\bof=/dev/", re.I),
            "Wrath: blocked dd to /dev/*",
        ),
        (
            re.compile(r"\bformat\s+[a-zA-Z]:\s*$", re.I),
            "Wrath: blocked format on drive letter",
        ),
        (
            re.compile(r"\brd\s+/s\s+/q\s+[a-zA-Z]:\\?\s*$", re.I),
            "Wrath: blocked rd /s /q on drive root",
        ),
        (
            re.compile(r"\bdel\s+(?:/[a-zA-Z]+\s+)+[a-zA-Z]:\\?\s*$", re.I),
            "Wrath: blocked del /s on drive root",
        ),
        (
            re.compile(r"\b(shutdown|reboot|poweroff)\b.*\b(-h\s+now|/s\s|/r\s)", re.I),
            "Wrath: blocked system shutdown/reboot",
        ),
        (
            re.compile(r"\bcipher\s+/w:", re.I),
            "Wrath: blocked cipher /w (secure wipe)",
        ),
        (
            re.compile(r"\bsudo\s+rm\s+-[a-zA-Z]*r[a-zA-Z]*f\s+/", re.I),
            "Wrath: blocked sudo rm -rf /",
        ),
    ]
    for pat, reason in deny_patterns:
        if pat.search(compact):
            return Decision(allow=False, reason=reason)

    # curl|bash / iwr|iex remote exec
    if not _env_truthy(PIPE_ENV):
        if re.search(
            r"(curl|wget)\b.+\|\s*(ba)?sh\b",
            low,
        ) or re.search(
            r"(iwr|invoke-webrequest|invoke-restmethod).+\|\s*(iex|invoke-expression)",
            low,
        ):
            return Decision(
                allow=False,
                reason=f"Wrath: blocked remote pipe-to-shell (set {PIPE_ENV}=1 to override)",
            )

    # git push --force to main/master
    if re.search(r"\bgit\s+push\b", low) and re.search(r"--force|--force-with-lease|-f\b", low):
        if re.search(r"\b(main|master)\b", low) and not _env_truthy(FORCE_ENV):
            return Decision(
                allow=False,
                reason=f"Wrath: blocked force-push to main/master (set {FORCE_ENV}=1 to override)",
            )
        # STRICT: deny any force-push when branch is not explicit in argv
        if _strict() and not re.search(r"\b(main|master)\b", low) and not _env_truthy(FORCE_ENV):
            return Decision(
                allow=False,
                reason=(
                    f"Wrath STRICT: blocked force-push without explicit branch in command "
                    f"(set {FORCE_ENV}=1 or unset {STRICT_ENV})"
                ),
            )
        if not _env_truthy(FORCE_ENV):
            return Decision(
                allow=True,
                warning=(
                    f"Wrath: force-push — confirm remote/branch. "
                    f"Override gate uses {FORCE_ENV}=1 for main/master. "
                    f"STRICT denies force-push when branch omitted."
                ),
            )

    # git reset --hard
    if re.search(r"\bgit\s+reset\s+--hard\b", low) and not _env_truthy(HARD_ENV):
        return Decision(
            allow=False,
            reason=f"Wrath: blocked git reset --hard (set {HARD_ENV}=1 to override)",
        )

    # git clean -fdx (wipes untracked)
    if re.search(r"\bgit\s+clean\b", low) and re.search(r"-[a-zA-Z]*f", low):
        if re.search(r"-[a-zA-Z]*x|-[a-zA-Z]*d", low) and not _env_truthy(CLEAN_ENV):
            return Decision(
                allow=False,
                reason=f"Wrath: blocked git clean -f[dx] (set {CLEAN_ENV}=1 to override)",
            )

    # git branch -D main/master
    if re.search(r"\bgit\s+branch\s+-[dD]\b", low) and re.search(r"\b(main|master)\b", low):
        return Decision(
            allow=False,
            reason="Wrath: blocked deleting main/master branch",
        )

    # warnings only
    if re.search(r"\bchmod\s+777\b", low):
        return Decision(
            allow=True,
            warning="Wrath: chmod 777 is usually wrong — prefer tighter perms.",
        )

    if re.search(r"remove-item\s+.*-recurse\s+.*-force", low) or re.search(
        r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f", low
    ):
        return Decision(
            allow=True,
            warning="Wrath: recursive force delete — double-check path.",
        )

    if re.search(r"\bDROP\s+(DATABASE|TABLE|SCHEMA)\b", compact, re.I):
        if _strict():
            return Decision(
                allow=False,
                reason="Wrath STRICT: blocked DROP DATABASE/TABLE/SCHEMA",
            )
        return Decision(
            allow=True,
            warning="Wrath: destructive SQL DROP — confirm target DB/table.",
        )

    if _strict() and re.search(r"\b(kubectl\s+delete|terraform\s+destroy)\b", low):
        return Decision(
            allow=False,
            reason=(f"Wrath STRICT: blocked infra destroy/delete (unset {STRICT_ENV})"),
        )

    return Decision(allow=True)
