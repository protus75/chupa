---
priority: P0
kind: bug
source: human
state: confirmed
---

## Depends on
- plan-bound-reject-release

## Context
- chupa/journal.py
- chupa/runner.py
- chupa/drain.py
- tests/test_journal.py
- tests/test_journal_roll.py
- tests/test_drain_upgrade.py
- tests/test_rework.py
- tests/test_storm.py
- tests/test_flake.py

## On-demand
- tests/test_storm_hold.py
- tests/test_kill_cli_activation.py

## Plan contract
- section 6.2

## Goal / Why
Two journal vocabularies become closed. A terminal's `dispatch` is a closed `Literal` that every consumer matches exhaustively. A `signal` body's name is a closed set that the journal write seam enforces, so an unknown value fails the build or the write and is never silently classified.

Why: section 6.2 promotes `dispatch` to a closed field with exhaustive consumers and closes `signal` names at the write seam. Today `dispatch` values are free strings written in `chupa/runner.py` and compared by string in `chupa/drain.py`. The constant `SPEC_GAP_HOLD` once served as both a dispatch value and a signal name, and two string-compared classifications of the same records diverged into a dispatch loop. `Journal.append` accepts any `signal` body.

## Scope in / Scope out
- In: `chupa/journal.py` defines `Dispatch = Literal["retry", "escalate", "reject_queue", "spec_gap_hold"]` and `dispatch_of(body) -> Dispatch | None`. It returns None when the key is absent and raises `ValueError` on any other value. Every consumer of a terminal's `dispatch` in `chupa/runner.py` and `chupa/drain.py`, and in `chupa/hardening.py` if it reads one, reads it through `dispatch_of` and branches with a `match` ending in `assert_never`. The writer in `chupa/runner.py` types each value it writes as `Dispatch`.
- In: `chupa/journal.py` defines `SIGNAL_NAMES`, the closed set of every signal name engine code writes. Enumerate it by grepping every `EventType.SIGNAL` and `"signal"` append site in `chupa/` and `eval/` (the eval harnesses write `review_baseline` and `diagnose_eval_start`; string literals and constants such as `INTAKE_SIGNAL`, `VERDICT_SIGNAL`, `HALT_SIGNAL`, `HANDOFF_SIGNAL`, `REWORK_ORDER`, `SUPERSEDES`, `WATCHER_PARSE_FAILURE`, `BASELINE_SIGNAL`, `ROUND_SIGNAL`, the thresh `signal` literals, and the `kind` values of flake, storm, control, kill, checkpoint, and merge-queue signals). `Journal.append` refuses, with a `ValueError` that names `SIGNAL_NAMES`, a `signal` body that does not carry exactly one of the keys `signal` or `kind` naming a member. Read-side tolerance of journals written earlier is unchanged.
- In: test fixtures that journal nameless or unlisted signal bodies (`{}`, `{"n": ...}`, `"unrelated"`, `"late"`, `"confirm"`, `"unknown"`, `"spec_gap_hold"`) are migrated to listed names. Each fixture's assertion stays the same.
- Out: body schemas beyond the name; read-side validation; any behavior change.

## Scope fence
- chupa/journal.py
- chupa/runner.py
- chupa/drain.py
- chupa/hardening.py
- tests/test_journal.py
- tests/test_journal_roll.py
- tests/test_drain_upgrade.py
- tests/test_rework.py
- tests/test_storm.py
- tests/test_storm_hold.py
- tests/test_flake.py
- tests/test_kill_cli_activation.py
- tests/test_vocabularies.py

## Acceptance criteria
1. `uv run pytest -q tests/test_vocabularies.py` exits 0. It includes `test_dispatch_vocabulary_is_closed`, which asserts `get_args(Dispatch)` equals the four section 6.2 values and that `dispatch_of` raises on `"other"`. It includes `test_every_engine_signal_name_is_listed`, which scans `chupa/` and `eval/` for literal signal and kind names written to `EventType.SIGNAL` and asserts each is in `SIGNAL_NAMES`. It includes `test_unknown_signal_name_is_refused_at_append`, which asserts that `{"signal": "spec_gap_hold"}`, `{}`, and a body carrying both `signal` and `kind` are each refused and nothing is written.
2. `uv run pytest -q tests/test_journal.py tests/test_journal_roll.py tests/test_drain_upgrade.py tests/test_rework.py tests/test_storm.py tests/test_storm_hold.py tests/test_flake.py tests/test_kill_cli_activation.py` exits 0.
3. `uv run pytest -q tests/test_drain.py tests/test_seed_path.py tests/test_hardening.py tests/test_daemon_composition.py` exits 0 unchanged.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_vocabularies.py
uv run pytest -q tests/test_journal.py tests/test_journal_roll.py tests/test_drain_upgrade.py tests/test_rework.py tests/test_storm.py tests/test_storm_hold.py tests/test_flake.py tests/test_kill_cli_activation.py
uv run pytest -q tests/test_drain.py tests/test_seed_path.py tests/test_hardening.py tests/test_daemon_composition.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_vocabularies.py -k test_unknown_signal_name_is_refused_at_append
```
- carries: tests/test_vocabularies.py

## Definition of rejected
Reject the branch if any engine code compares a `dispatch` value as a bare string outside `dispatch_of`, if `SIGNAL_NAMES` lists a name no engine code writes, if any fixture assertion is weakened to pass, or if the regression test passes on the merge base.

## Time budget
- expected: 60m
- stuck: 150m
