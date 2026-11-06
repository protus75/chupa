---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/__main__.py
- dev.py
- vscode-chupa/extension.js
- tests/test_control_cli.py
- docs/how-chupa-works.md

## Goal / Why
`chupa confirm` and `chupa reject` refuse unless stdin is an interactive terminal, then wait for `y`. The operator's VS Code extension (`vscode-chupa`) offers Confirm and Reject on a held ticket's right-click menu. That click is the person's decision, but today it can only open a terminal running `./dev.py confirm <stem>` and wait for a typed `y`. Faking a terminal to answer `y` would bypass the guard instead of changing it, so it was rejected (2026-11-06).

After this change, a `--yes` flag on `confirm` and `reject` skips the terminal check and the prompt. Without `--yes` the behavior is unchanged. The verdict journals exactly as it does after a typed `y`.

## Scope in / Scope out
- In: `chupa/__main__.py`:
  - `confirm` and `reject` accept `--yes`;
  - with it, `main` skips the `isatty` refusal and `_verdict` skips `read_input`, proceeding as if `y` were answered;
  - without it, nothing changes.
- In: `dev.py`: `confirm` and `reject` accept `--yes` and pass it to every per-stem `chupa` call.
- In: `vscode-chupa/extension.js`: the Confirm and Reject menu commands run `./dev.py confirm|reject <stem> --yes`.
- In: tests in `tests/test_control_cli.py`:
  - `--yes` keeps a Reject-queue ticket with `terminal=(lambda: False, <reader that raises>)`;
  - without `--yes`, the same non-terminal call is refused with "verdict requires an interactive terminal";
  - `reject --yes` stamps the ticket rejected.
- In: docs.
  - `docs/how-chupa-works.md` section 2.1 `confirm` and `reject` rows: name `--yes`.
  - Section 2.2: the `confirm` and `reject` rows take `--yes`.
  - Section 6.6: replace "type the exact stem" with the current `y` prompt, plus one sentence on `--yes`.
- Out: the journal body of a verdict, `runner.verdict`, every other verb, and the rule in CLAUDE.md that sessions may not run `confirm` or `reject`.

## Scope fence
- chupa/__main__.py
- dev.py
- vscode-chupa/extension.js
- tests/test_control_cli.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest -q tests/test_control_cli.py` exits 0, including the three tests above.
2. `docs/how-chupa-works.md` sections 2.1, 2.2 and 6.6 describe `--yes` and the `y` prompt.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_control_cli.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if a verdict without `--yes` proceeds off a terminal, if `--yes` changes what the journal records, or if anything fakes a terminal.

## Time budget
- expected: 25m
- stuck: 75m
