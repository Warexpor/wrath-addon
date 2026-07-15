# Grok Build hook contract (Wrath V2)

Source: `~/.grok/docs/user-guide/10-hooks.md` + production use of Wrath 1.x.

## Runner behavior

- Hooks receive **JSON on stdin**; blocking hooks write **JSON on stdout**.
- **Fail-open**: crash/timeout/malformed output does **not** deny. Only explicit
  `{"decision":"deny","reason":"..."}` blocks (any exit code if stdout deny is present).
- Exit `2` is also documented as explicit deny for blocking hooks.
- Env (always): `GROK_HOOK_EVENT`, `GROK_HOOK_NAME`, `GROK_SESSION_ID`,
  `GROK_WORKSPACE_ROOT`, `CLAUDE_PROJECT_DIR`.
- Plugin hooks also get: `GROK_PLUGIN_ROOT`, `GROK_PLUGIN_DATA` (+ Claude aliases).

## PreToolUse input (typical)

```json
{
  "hookEventName": "pre_tool_use",
  "sessionId": "…",
  "cwd": "…",
  "workspaceRoot": "…",
  "toolName": "run_terminal_command",
  "toolInput": { "command": "…" },
  "toolUseId": "…",
  "toolInputTruncated": false,
  "timestamp": "…"
}
```

## PreToolUse output

- Allow: `{"decision":"allow"}` optional `systemMessage` for soft warn.
- Deny: `{"decision":"deny","reason":"…"}`.

## Passive events + systemMessage

Official doc text says passive events ignore stdout. **In practice** Grok Build
honors `systemMessage` on SessionStart, UserPromptSubmit, and Stop (Wrath 1.x
depends on this). V2 continues that contract; if a release drops it, drive pack
degrades silently (hooks still journal).

## Events Wrath V2 registers

SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure,
Stop, StopFailure, PermissionDenied, SubagentStart, SubagentStop,
PreCompact, PostCompact, SessionEnd.

## Tool name aliases (matcher + parsing)

| Alias | Canonical |
|-------|-----------|
| Bash / Shell | run_terminal_command |
| Read | read_file |
| Edit / Write / MultiEdit | search_replace / write |
| Task | spawn_subagent |
| MCP | `server__tool` qualified name |
