---
name: wrath-review
description: Adversarial high-signal review of recent changes. Use for /wrath-review, "review this", pre-PR review, or "what did we break".
---

# wrath-review

1. Scope: `git diff` / staged / named paths. If none, ask one path question.
2. Report only **high-signal** issues: bugs, security, data loss, broken contracts. Skip style nits and praise.
3. Format each finding: `file:line` · severity · one-line problem · one-line fix.
4. Confidence filter: skip guesses. If zero findings: `no high-signal issues.`
5. Optional: spawn agent `wrath-reviewer` for large diffs; keep the final list tight.
