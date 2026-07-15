"""Bulk repo / home upload heuristics."""

from __future__ import annotations

import re

from wrath.policy.decision import Decision

# Patterns that look like packaging whole repos / home for upload
_BUNDLE = re.compile(
    r"\bgit\s+bundle\s+create\b|"
    r"\bgit\s+archive\b.*\b(HEAD|--all)\b|"
    r"\btar\s+[czjf]*\s+.*\s+(\$home|~|/home/|/Users/)\b|"
    r"\bCompress-Archive\b.*(\$home|\$env:userprofile|\\\\Users\\\\)\b|"
    r"\bzip\s+-r\b.*\s+(\.|~|\$home)\b|"
    r"\bgcloud\s+storage\s+cp\s+-r\b|"
    r"\baws\s+s3\s+sync\b.*\s+(s3://)\b|"
    r"\bgsutil\s+-m\s+cp\s+-r\b|"
    r"\brclone\s+sync\b|"
    r"\bcurl\b.+\b--upload-file\b.+\.(bundle|tar|zip|tgz)\b",
    re.I,
)


def check_privacy_upload(cmd: str, mode: str = "warn") -> Decision | None:
    if mode in ("", "off", "none"):
        return None
    if not cmd or not _BUNDLE.search(cmd):
        return None
    if mode == "deny":
        return Decision(
            allow=False,
            reason=(
                "Wrath privacy: blocked bulk pack/upload pattern "
                "(git bundle/archive, home tar/zip, cloud sync). "
                "Set profile off or privacy_upload=warn."
            ),
            rule_id="privacy_upload",
            severity="deny",
        )
    return Decision(
        allow=True,
        warning=(
            "Wrath privacy: bulk pack/upload pattern — confirm you intend to "
            "send a full repo or home tree off-machine."
        ),
        rule_id="privacy_upload_warn",
        severity="warn",
    )
