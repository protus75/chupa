---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/mergequeue.py
- chupa/merge.py
- chupa/stages.py
- chupa/config.py
- tests/test_mergequeue.py
- tests/test_merge.py
- tests/test_stages.py

## Goal / Why
A host declares its own checks under `review.mechanical` (`code`, `argv`, `trigger: always | list[path-prefix]`, `severity: hard | soft`). Config accepts them, but only the daemon merge queue runs any (`MergeQueue.host_checks` in `chupa/mergequeue.py`, `always` + `hard` entries only, at merge). Check never runs them, `drain`/`run` merges (`merge` in `chupa/merge.py`) never run them, and path-triggered or soft entries never run anywhere: a declared check is silently skipped.

## Scope in / Scope out
- In: ONE host-check runner. Move the command execution in `MergeQueue._command` into `chupa/stages.py` as the single function that runs one `review.mechanical` entry: `ctx.exec_.run` with `cwd` the ticket worktree, `env=child_env(ctx.env, ctx.config)`, `timeout=ticket.stuck_minutes * 60.0`, spool write, scrubbed `OUTPUT_TAIL_CHARS` tail, and the existing timeout and missing-executable findings. `MergeQueue` calls it in place of its own copy; its selection rules, spool names, and behavior stay as they are.
- In: Check runs every TRIGGERED entry after the engine gates, in config order. Triggered means `trigger: always`, or any committed changed file matching a listed prefix by the scope-fence path rule (`_in_fence`: equal, or a descendant after `/`; `chupa/x` does not match `chupa/xy.py`). Each run yields one `GateReport` with the entry's `code`, recorded in `checks.json`, and spool `check/host-<nn>.txt` (`nn` = 1-based entry index). A hard failure fails Check `gate_failed`; a soft failure records `fail` and its findings on the stage result, and Check proceeds. A failing entry is re-run at the merge base exactly as Verification's base-diff attribution does; red at base is pre-existing (filed as a second problem, charged to neither Check nor retry).
- In: inline merge (`merge` in `chupa/merge.py`) runs every triggered HARD entry on the rebased candidate through the same runner, spool `merge/host-<nn>.txt`; any failure refuses admission with main untouched.
- In: an untriggered entry leaves no command, report, spool, or finding.
- In: `tests/test_host_mechanical.py` covers, through production Check and inline merge: `test_triggered_entries_run_at_check`, `test_untriggered_entry_never_runs` (including `chupa/x` against `chupa/xy.py`), `test_hard_failure_fails_check`, `test_soft_failure_reported_and_passes`, `test_base_red_entry_is_preexisting`, `test_timeout_and_missing_executable_fail_closed` (provider keys absent from the child env, secrets scrubbed from spool and findings), and `test_inline_merge_reruns_triggered_hard_entries` (soft and untriggered entries excluded; a red hard entry refuses without moving main).
- Out: config schema, ticket validation, `gate_bypass` (host check codes are not bypass codes), Suggestion Box messages for soft failures, `review.surfaces`, and the merge queue's selection rules.

## Scope fence
- chupa/stages.py
- chupa/merge.py
- chupa/mergequeue.py
- tests/test_host_mechanical.py
- tests/test_stages.py
- tests/test_merge.py

## Acceptance criteria
1. `uv run pytest -q tests/test_host_mechanical.py` exits 0 with every test named above.
2. `uv run pytest -q tests/test_mergequeue.py` exits 0 with that file unchanged, proving the merge queue keeps its behavior on the shared runner.
3. `chupa/mergequeue.py` no longer calls `ctx.exec_.run` for host checks; the only host-check execution is the shared function in `chupa/stages.py`.
4. `uv run pytest -q` exits 0. `tests/test_stages.py` and `tests/test_merge.py` change only where an existing assertion contradicts host checks now running.

## Verification
```
uv run pytest -q tests/test_host_mechanical.py
uv run pytest -q tests/test_mergequeue.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if host-check execution exists in more than one place, if an untriggered entry leaves any trace, if a soft failure blocks Check or merge, if a red hard entry lets a merge through, or if `tests/test_mergequeue.py` changes.

## Time budget
- expected: 60m
- stuck: 120m
