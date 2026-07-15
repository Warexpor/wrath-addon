---
name: wrath-ship
description: Finish work for ship/commit/PR. Use for /wrath-ship, ready to commit, wrap up branch, or pre-PR checklist.
---

# wrath-ship

1. `git status` + `git diff` (and staged) — summarize real changes.
2. Run the project’s tests/build for touched areas (wrath-check rules).
3. Draft a commit message: complete sentences, why + what, no fake coauthors.
4. Do **not** commit or push unless the user explicitly asked.
5. If they asked to commit: stage only relevant files, commit, show hash.
6. Hard-to-reverse (force push, reset --hard): refuse unless they reconfirm; Wrath hooks may already block.
