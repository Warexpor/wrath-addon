from __future__ import annotations

import re

from wrath.io import looks_like_secret_path
from wrath.policy.decision import Decision


def check_secret_write(path: str, tool_input: dict) -> Decision | None:
    if not path or not looks_like_secret_path(path):
        return None
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
            rule_id="secrets_paste",
            severity="deny",
        )
    return Decision(
        allow=True,
        warning="Wrath: sensitive path — do not print secrets to chat or remote pastes.",
        rule_id="secrets_path",
        severity="warn",
    )


def check_secret_url(tool_input: dict) -> Decision | None:
    url = str(tool_input.get("url") or tool_input.get("uri") or "")
    body = str(tool_input.get("body") or tool_input.get("content") or "")
    if url and body and re.search(r"(api[_-]?key|secret|password|private_key)\s*[:=]", body, re.I):
        if re.search(r"pastebin|gist\.github|webhook\.site", url, re.I):
            return Decision(
                allow=False,
                reason="Wrath: blocked posting credential-like body to public paste/webhook URL",
                rule_id="secrets_url",
                severity="deny",
            )
    return None
