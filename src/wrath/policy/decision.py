from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    allow: bool
    reason: str = ""
    warning: str = ""
    rule_id: str = ""
    severity: str = ""  # info | warn | deny

    def as_hook_dict(self) -> dict:
        if not self.allow:
            return {
                "decision": "deny",
                "reason": self.reason or "blocked by Wrath",
            }
        out: dict = {"decision": "allow"}
        if self.warning:
            out["systemMessage"] = self.warning
        return out
