---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
none

## Context
- docs/how-chupa-works.md
- chupa/__main__.py
- chupa/runner.py
- tests/test_control_cli.py
- tests/test_reject_queue.py

## Goal / Why
`confirm` (keep) and `reject` (kill) are the operator's verdicts, and a keep resets a lineage's spine caps. Today any process can run them and the journal records `actor: operator`: an agent session ran `confirm phase7-continue` twice after diagnosis said reject, resetting its caps each time. Only a person at a terminal may give a verdict.

## Scope in / Scope out
- In: the `confirm` and `reject` CLI verbs in `chupa/__main__.py` refuse unless stdin is an interactive terminal (`isatty()`), before any lock, journal read, or control-inbox request, with exit 2 and the paved road "a human runs this in a terminal: ./dev.py confirm|reject <stem>".
- In: on a terminal, the verb prints the stem and its Reject-queue reason (or draft / held-admission state), then asks the person to type the stem; anything other than the exact stem aborts with exit 1 and changes nothing.
- In: the terminal check and prompt read through one injectable seam in `chupa/__main__.py` (an `isatty` predicate and an input reader), so tests drive both paths without a real terminal.
- In: `./dev.py` gains a `confirm STEM...` subcommand matching `reject`, passing stdin through so the prompt reaches the person.
- In: tests add `test_verdict_refused_without_terminal` (both verbs, no journal or inbox write) and `test_verdict_requires_typed_stem` (exact stem proceeds; a mismatch or empty answer aborts unchanged); existing CLI tests that run these verbs supply the seam as a terminal answering the stem.
- In: update `docs/how-chupa-works.md` sections 2.1, 2.2 (`./dev.py confirm`), and 6.6 (keep and kill require a person at a terminal typing the stem), so the doc matches the code when this merges.
- In: if `uv run pytest -q` fails only on tests that also fail on the merge base, those failures are pre-existing: Check excuses them (base-red). Commit the work and list them in the run record; never stop with `premise_failed` for them.
- Out: `runner.verdict` semantics, the control-inbox request format, the machine actor's scripted confirms in the Phase 6 exit harness, and cap rules.

## Scope fence
- docs/how-chupa-works.md
- chupa/__main__.py
- dev.py
- tests/

## Acceptance criteria
1. `uv run pytest -q tests/test_control_cli.py tests/test_reject_queue.py` exits 0, including `test_verdict_refused_without_terminal` and `test_verdict_requires_typed_stem`.
2. `uv run pytest -q` exits 0.
3. `docs/how-chupa-works.md` sections 2.1, 2.2 and 6.6 say keep and kill need a person at a terminal typing the stem, and list `./dev.py confirm`.

## Verification
```
uv run pytest -q tests/test_control_cli.py tests/test_reject_queue.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if either verb can change state without an interactive terminal and the typed stem, if the refusal writes anything, or if `runner.verdict` or the control-inbox format changes.

## Time budget
- expected: 45m
- stuck: 90m
