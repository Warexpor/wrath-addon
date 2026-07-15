---
name: wrath-profile
description: Switch Wrath profile (default thin strict privacy fleet max). Use for /wrath-profile.
---

# Wrath profile

1. Parse target: `default` | `thin` | `strict` | `privacy` | `fleet` | `max`.
2. MCP `wrath_set_profile` with that name (applies mode flags from profile defaults).
3. Confirm with `wrath_status`.

Phrase: `/wrath-profile fleet` or “wrath profile privacy”.
