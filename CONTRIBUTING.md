# Contributing

## Dev loop

```powershell
python -m pytest tests -q
.\install.ps1   # refresh Grok install + MCP absolute path
```

- Hooks and MCP are **stdlib only** (no pip deps at runtime).
- Tests may use pytest.
- Keep policy pure (no I/O except env) so unit tests stay fast.
- Prefer small, root-cause diffs. Open an issue for large design changes.

## License

By contributing you agree your changes are licensed under **GPL-3.0-or-later** (same as this repository).
