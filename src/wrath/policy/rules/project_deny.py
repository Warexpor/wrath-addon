from __future__ import annotations

import re

from wrath.config import EffectiveConfig
from wrath.policy.decision import Decision


def check_project_deny(cmd: str, config: EffectiveConfig | None) -> Decision | None:
    if not config or not config.deny or not cmd:
        return None
    for pat_s in config.deny:
        try:
            if re.search(pat_s, cmd, re.I):
                return Decision(
                    allow=False,
                    reason=f"Wrath: blocked by project deny pattern /{pat_s}/",
                    rule_id="project_deny",
                    severity="deny",
                )
        except re.error:
            continue
    return None
