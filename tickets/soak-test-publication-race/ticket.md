---
state: confirmed
source: human
priority: P0
kind: chore
---

## Depends on
- none

## Context
- tests/integration/test_daemon_soak_runner.py::test_daemon_soak_runs_production_serve
- chupa/serve.py::Serve.publish
- chupa/tickets.py::ticket_path
- chupa/tickets.py::parse_ticket
- chupa/daemon.py::apply_rework
- eval/daemon_soak.py::_Member.ticket
- docs/how-chupa-works.md#7.2

## Goal / Why
`tests/integration/test_daemon_soak_runner.py::test_daemon_soak_runs_production_serve` fails intermittently in the full parallel suite. Each failure fails an unrelated ticket's Check or Merge and costs it a retry (`pypi-readme-user-guide` lost 2 of 3 retries to it on 2026-11-10). `soak-serve-stops-early-under-load` added the engine-log tail to the refusal and left the cause open. That tail now names the cause:

```
{"event": "stage_start", "stem": "unresolved", "attempt": 1, "surface": "merge"}
{"event": "worker_failure", "error": "assert {'Depends on'...} == {'Depends on'...}\n  Differing items:\n  {'Goal / Why': 'Resolve against current main.'} != {'Goal / Why': 'Exercise synthetic production work.'}"}
{"event": "serve_cleanup_failed", ...}
eval.daemon_soak.SoakRefused: conflict_resolution_rungs: serve stopped early (1)
```

The failing assertion is the test's own `offered` spy: `assert owner.published[ticket.stem][0].sections == ticket.sections`. In the `conflict_resolution_rungs` member, Rework rewrites the `unresolved` ticket (`eval/daemon_soak.py`, `corrected=True`), and attempt 1 is offered to the merge queue with the corrected text. `Serve.published` is the watcher's snapshot, refreshed on a 0.1s debounced poll (`docs/how-chupa-works.md` section 7.2). Under load the offer can happen before the watcher's next poll, so the snapshot still holds the old text. Nothing on the merge path reads `Serve.published`: it is read only by serve's dispatch, which already detects a stale snapshot by blob sha, and by serve's confirm. The spy therefore demands an invariant the engine neither promises nor needs.

After this change, the spy checks only what the engine guarantees, the test passes whatever the watcher's timing, and the test proves this by forcing the stale case on every run.

## Scope in / Scope out
- In: in `test_daemon_soak_runs_production_serve`, replace the `owner.published[...]` assertion in `offered` with one the engine guarantees: the offered ticket's `sections` equal `parse_ticket` of the ticket file on disk in that member's checkout (`<member repo>/` + `ticket_path(stem)`). `apply_rework` writes and commits that file before the corrected attempt runs. If that does not hold at offer time either, delete the assertion instead and say why in the run record.
- In: in the same test, make the stale case deterministic. Wrap `Serve.publish` (via `monkeypatch`) so the watcher's publication of the corrected `unresolved` ticket is held back until after `MergeQueue.offer` has been called for `("unresolved", 1)`, then released. Record that the hold happened, and assert it did, so the test cannot pass by never reaching the stale window.
- Out: `chupa/` code. If the investigation shows the engine must keep `Serve.published` equal to the offered ticket at merge time, stop and report a premise failure naming the code that reads it; do not change the engine here.
- Out: raising timeouts, adding retries, skips, or flaky marks; `eval/daemon_soak.py`; other members and other tests.

## Scope fence
- tests/integration/test_daemon_soak_runner.py

## Acceptance criteria
1. `tests/integration/test_daemon_soak_runner.py` no longer reads `owner.published`; `grep -n 'published\[' tests/integration/test_daemon_soak_runner.py` prints nothing.
2. In `tests/integration/test_daemon_soak_runner.py`, `test_daemon_soak_runs_production_serve` holds back publication of the corrected `unresolved` ticket until after its attempt-1 offer, and asserts the hold occurred. On the base commit's spy, the same hold makes the test fail with the `Goal / Why` mismatch above. That rules out a hold that never reaches the stale window. Record the base-commit failure line in the run record.
3. `./dev.py test tests/integration/test_daemon_soak_runner.py` exits 0.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_daemon_soak_runner.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- any file other than `tests/integration/test_daemon_soak_runner.py` changes;
- the test gains a skip, a flaky or retry mark, a longer timeout, or a sleep;
- the forced stale-publication case is missing, or the test does not assert that the hold happened.

## Time budget
- expected: 30m
- stuck: 90m
