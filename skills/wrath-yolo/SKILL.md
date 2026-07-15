---
name: wrath-yolo
description: Enable Wrath YOLO soft-guard profile. Use for /wrath-yolo, yolo on/off, unrestricted footguns.
---

# Wrath YOLO

Opposite of `max` / privacy. Soft guards for trusted sessions.

1. Prefer MCP `wrath_set_yolo` with `yolo: true` (or `wrath_set_profile` profile=`yolo`).
2. Confirm with `wrath_status` — `yolo: true`, `profile: yolo`.
3. Off: `yolo: false` or `/wrath-profile default`. Env `WRATH_YOLO=1` forces on.

**Allowed when YOLO:** force-push, `reset --hard`, `clean -fdx`, curl|sh, bulk pack/upload.  
**Still blocked:** root/home wipe, mkfs/dd, fork bomb, `.git/` writes, secrets→public paste, project `deny`.

One-line blast-radius confirm; do not leave YOLO on by default.
