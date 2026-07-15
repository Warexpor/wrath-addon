---
name: wrath-check
description: Verification protocol before claiming done. Use for /wrath-check, /check, "verify", "are we done", or when about to say fixed/passing without evidence.
---

# wrath-check

Before any "done/fixed/passing" claim:

1. State the success criterion in one line.
2. Run the **real** project check (test/build/lint the touched package). Prefer existing scripts in README/package.json/pyproject.
3. Paste the command + exit code + relevant tail of output.
4. If you cannot run it, say exactly why and what the user should run.
5. No test theater: do not hardcode expected values in fake tests; do not reimplement the SUT inside the test.

If checks fail: fix root cause, re-run, then report.
