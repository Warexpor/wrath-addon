# Security

Wrath is a **heuristic** PreToolUse + lifecycle guard for Grok Build, not an OS sandbox.

## V2 coverage

- Destructive shell / git footguns (including nested powershell/bash/cmd unwrap)
- Project deny regexes
- Secret-path paste heuristics
- Privacy bulk pack/upload patterns (profile-dependent)
- Orchestrate spawn without `model=` (warn/deny)
- Journal of Wrath denials **and** harness `PermissionDenied`

## Residual risk

- Advanced PowerShell, deep nesting beyond configured depth, obfuscated commands can slip past.
- Fail-open: hook crash/timeout does **not** deny.
- Privacy mode is **not** a network sandbox and does not replace Grok’s own sandbox settings.
- Server-side model traffic is outside Wrath’s control.

Prefer OS permissions and human review for high-stakes work.

## Report issues

Open a GitHub issue on [Warexpor/wrath-addon](https://github.com/Warexpor/wrath-addon) with:

- The command / tool payload that should have been blocked (or was blocked incorrectly)
- Wrath version (`plugin.json` or MCP `wrath_doctor`)
- Profile / overrides (`WRATH_ALLOW_*`, `WRATH_STRICT`, `WRATH_PRIVACY`)

Do not paste real secrets into issues.
