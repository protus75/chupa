---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: draft
---

## Depends on
- none

## Context
- chupa/stages.py::_lift_files
- chupa/stages.py::lift_outbox
- chupa/redact.py
- tests/integration/test_stages.py
- docs/how-chupa-works.md#3.3 What the engine writes back

## Goal / Why
`lift_outbox` commits files from the agent-writable worktree outbox straight to `main`. Nothing runs between the agent and that commit: no scope fence, no Review, no Redactor. `_lift_files` filters only by `only`, `ticket.md`, the KNOWN_ARTIFACTS name check and byte-equality with the canonical copy. The `run-record` lift (after Implement) and the `review` lift pass `only=None`, so every other file under the worktree's `tickets/<stem>/` is lifted. `src.read_bytes()` also follows symlinks. An Implement agent that holds its provider key can write the key, or a symlink to a secret file, into the outbox. It then lands on `main`, which the checkpoint push later publishes.

CLAUDE.md section A says "Fenced by gates, not jailed" and "configured secret values are redacted from every captured stream at the write seam". This lift is a write seam that has neither. After this change each lift commits only the artifact the engine names for it, refuses symlinks, and scrubs the content through `ctx.driver.redactor` before writing.

Simplest approach: derive the artifact name inside `_lift_files`, so no caller changes. The rejected alternative is threading a new `only=` argument through every caller, which leaves direct `lift_outbox` callers in tests unprotected.

## Scope in / Scope out
In:
- Selection rule in `_lift_files`: when `only` is given, it alone selects the file, for any kind (this covers `diagnosis`, `harvest` and `harvest-rework`). When `only` is None, `run-record` takes only `run.md`, `review` takes only `review.md`, and `checks` takes only `checks.json` plus registered KNOWN_ARTIFACTS names.
- `_lift_files` skips symlinks.
- `lift_outbox` writes the `ctx.driver.redactor` scrubbed text rather than the raw bytes.
- Integration tests for the three behaviours, unit tests for the selection and symlink lines in `_lift_files`, and a doc sentence.

Out:
- Gate and fence changes.
- Journal scrubbing.
- Read-only tool restriction, which is covered by `claude-readonly-hard-tool-restriction`.
- Any change to the `lift_outbox` signature.

## Scope fence
- chupa/stages.py
- tests/integration/test_stages.py
- tests/unit/test_lift_files.py
- docs/how-chupa-works.md

## Acceptance criteria
1. With an extra file `notes.txt` and a symlink in the outbox, the `run-record` lift commits only `run.md`. The test asserts `notes.txt` is absent from the commit and from `tickets/<stem>/` on `main`; a test that also passes when `notes.txt` is committed checks nothing. Checked by `-k outbox_lift` in `./dev.py test tests/integration/test_stages.py -k outbox_lift`.
2. A symlinked `run.md` pointing at a file holding a secret is not committed. The test asserts the target's content appears nowhere on `main`. Checked by `-k outbox_lift` in `./dev.py test tests/integration/test_stages.py -k outbox_lift`.
3. A named artifact containing the configured secret value `FAKE_KEY` is committed with `[REDACTED:FAKE_KEY]` in its place. The test asserts the raw secret is absent from the committed blob, ruling out a verbatim copy. Checked by `-k outbox_lift` in `./dev.py test tests/integration/test_stages.py -k outbox_lift`.
4. The unit tests `test_lift_files_selects_named_artifact_per_kind`, `test_lift_files_skips_symlink` and `test_lift_files_only_overrides_kind` in `./dev.py test tests/unit/test_lift_files.py` run the per-kind selection and symlink-skip lines. The last one passes `kind="harvest-rework"` with `only` set and asserts that file is selected, ruling out a closed kind table that drops it. The per-kind test asserts a `review` lift does not select `run.md`.
5. The existing `checks` and `review` lift tests still pass with `./dev.py test tests/integration`.
6. `docs/how-chupa-works.md` section 3.3 states the lift "refuses symlinks". Checked by `grep -n "refuses symlinks" docs/how-chupa-works.md`, a phrase only the new sentence contains.

## Verification
```
./dev.py test tests/integration/test_stages.py -k outbox_lift
./dev.py test tests/unit/test_lift_files.py
./dev.py test tests/integration
grep -n "refuses symlinks" docs/how-chupa-works.md
```

## Definition of rejected
A lift kind still commits an unnamed file or a symlink target, or a `harvest-rework` lift with `only` set commits nothing. Or the fix needs a gate, config knob or signature change beyond the named files.

## Time budget
- expected: 40m
- stuck: 80m
