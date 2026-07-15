from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Decision:
    allow: bool
    reason: str = ""
    warning: str = ""
    rule_id: str = ""
    severity: str = ""  # info | warn | deny
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def as_hook_dict(self) -> dict:
        if not self.allow:
            return {
                "decision": "deny",
                "reason": self.reason or "blocked by Wrath",
            }
        out: dict = {"decision": "allow"}
        msg = self.warning
        if self.warnings and not msg:
            msg = self.warnings[0]
        elif self.warnings and msg:
            msg = f"{msg} {self.warnings[0]}".strip()
        if msg:
            out["systemMessage"] = msg
        return out

    def with_warning(self, warning: str) -> Decision:
        if not warning:
            return self
        w = self.warning
        combined = f"{w} {warning}".strip() if w else warning
        return Decision(
            allow=self.allow,
            reason=self.reason,
            warning=combined,
            rule_id=self.rule_id or "warn",
            severity=self.severity or "warn",
            warnings=self.warnings + (warning,),
        )
