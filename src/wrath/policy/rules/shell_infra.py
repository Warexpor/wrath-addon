from __future__ import annotations

import re

from wrath.policy.decision import Decision


def check_infra(cmd: str, *, strict: bool = False) -> Decision | None:
    compact = " ".join(cmd.split())
    low = compact.lower()
    if re.search(r"\bDROP\s+(DATABASE|TABLE|SCHEMA)\b", compact, re.I):
        if strict:
            return Decision(
                allow=False,
                reason="Wrath STRICT: blocked DROP DATABASE/TABLE/SCHEMA",
                rule_id="sql_drop",
                severity="deny",
            )
        return Decision(
            allow=True,
            warning="Wrath: destructive SQL DROP — confirm target DB/table.",
            rule_id="sql_drop_warn",
            severity="warn",
        )
    if strict and re.search(r"\b(kubectl\s+delete|terraform\s+destroy)\b", low):
        return Decision(
            allow=False,
            reason="Wrath STRICT: blocked infra destroy/delete",
            rule_id="infra_destroy",
            severity="deny",
        )
    return None
