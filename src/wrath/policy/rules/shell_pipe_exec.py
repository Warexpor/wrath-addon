from __future__ import annotations

import os
import re

from wrath.policy.decision import Decision

PIPE_ENV = "WRATH_ALLOW_PIPE_EXEC"


def check_pipe_exec(cmd: str) -> Decision | None:
    if os.environ.get(PIPE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}:
        return None
    low = " ".join(cmd.split()).lower()
    if re.search(r"(curl|wget)\b.+\|\s*(ba)?sh\b", low) or re.search(
        r"(iwr|invoke-webrequest|invoke-restmethod).+\|\s*(iex|invoke-expression)",
        low,
    ):
        return Decision(
            allow=False,
            reason=f"Wrath: blocked remote pipe-to-shell (set {PIPE_ENV}=1 to override)",
            rule_id="pipe_exec",
            severity="deny",
        )
    return None
