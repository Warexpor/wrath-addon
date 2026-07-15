---
name: wrath-privacy
description: Enable Wrath privacy mode (bulk upload deny). Use for /wrath-privacy, privacy on/off.
---

# Wrath privacy

1. Call MCP `wrath_set_privacy` with `privacy: true` (or false for off).
2. Confirm with `wrath_status` — expect `privacy: true` and bulk pack patterns denied.
3. Env `WRATH_PRIVACY=1` forces on. Profile `privacy` / `max` also sets this.

Do not claim network sandboxing — heuristic client-side policy only.
