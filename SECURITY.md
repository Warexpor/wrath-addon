# Security

Wrath is a **heuristic** PreToolUse guard for Grok Build, not a sandbox.

## Report issues

Open a GitHub issue on [Warexpor/wrath-addon](https://github.com/Warexpor/wrath-addon) with:

- The command / tool payload that should have been blocked (or was blocked incorrectly)
- Wrath version (`plugin.json` or MCP `wrath_doctor`)
- Whether overrides (`WRATH_ALLOW_*`, `WRATH_STRICT`) were set

Do not paste real secrets into issues.

## Residual risk

Advanced PowerShell, nested shells, and omitted branch names on force-push can still slip past patterns. Prefer OS permissions and review for high-stakes work.
