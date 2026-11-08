---
state: confirmed
source: human
priority: P0
kind: feature
---

## Depends on
- none

## Runs before
- review-alongside-drain

## Context
- chupa/lockfile.py
- chupa/journal.py::Journal
- chupa/__main__.py::_review
- chupa/__main__.py::_verdict
- chupa/runner.py::verdict
- chupa/llm.py::FakeLLM
- chupa/reconcile.py::orphans
- chupa/llmeffect.py::llm_key
- chupa/requisition.py
- tests/integration/test_review_command.py
- docs/how-chupa-works.md#2.1 Verbs

## Goal / Why
While `./dev.py review A` waits on its model call, `./dev.py confirm B` for a different ticket fails. On 2026-11-08 the operator could not confirm a ticket while another ticket's review was running. Cause: one checkout lock (`chupa.lock`) guards two resources, git writes to `main` and journal appends. `_review` takes the lock before intake and keeps it through the model call, because the provider session appends to the journal during the call (thresh signals, timers, drought transitions), and `Journal.append` is safe only for a single writer (torn-tail repair and segment roll). After this change, journal appends get their own short-held lock, and `review` holds the checkout lock only for intake and the reads that follow it. While a review's model call is in flight, the checkout lock is free, so `confirm` and `reject` of other tickets run immediately.

## Scope in / Scope out
- In: `chupa/journal.py`. `Journal.append` holds an exclusive `flock` on `<state_dir>/journal.lock` across torn-tail repair, segment roll and the write. Every append repairs the tail under that lock, because a torn tail can now come from another process that died mid-write. This replaces the once-per-handle `_tail_repaired` flag.
- In: `chupa/__main__.py::_review`. Acquire the checkout lock, run intake and the checks that read `main` and the journal, then release it before building the provider session. The model call and the `requisition_verdict` append run without the checkout lock.
- In: `chupa/reconcile.py::orphans`. Ignore effect intents whose key belongs to the on-demand review slot (`llm/review-<stem>/...`, from `stem_slot=f"review-{stem}"` in `_review`). With the lock free, a drain, run or serve started during a review's model call must not count that call as an orphaned run and reap the ticket to `abandoned`.
- In: `tests/integration/test_reconcile.py`. A journal holding an open `llm/review-<stem>/...` intent yields no orphan for that stem, and an open drain-slot intent for the same stem still does.
- In: `tests/integration/test_review_command.py`. A review whose FakeLLM reply is a callable that calls `Lockfile(state_dir, ...).acquire()` and then `release()` succeeds with the lock acquired, not with `LockHeld`. While holding the lock, the callable also runs `reconcile.orphans` on the journal. The reviewed stem is not in the result, and after the review its last state is unchanged and its `requisition_verdict` is journaled.
- In: `tests/integration/test_journal.py`. Two processes each append 200 events to the same state dir at the same time, and `Journal.read()` afterwards returns all 400 with none torn or lost.
- In: `tests/integration/test_storm_producer.py`. The state-dir listing at line 279 now includes `journal.lock`.
- In: `docs/how-chupa-works.md` section 2.1. The `review` row says the lock is held for intake only, and the doc states that journal appends take `journal.lock`.
- Out: `triage`, which also holds the lock across a model call; drain and serve lock lifetimes; `confirm`'s control-request fallback and the `control/active.json` lifecycle; `review` while a drain holds the lock (ticket `review-alongside-drain`).

## Scope fence
- chupa/journal.py
- chupa/__main__.py
- chupa/reconcile.py
- tests/integration/test_reconcile.py
- tests/integration/test_review_command.py
- tests/integration/test_journal.py
- tests/integration/test_storm_producer.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_review_command.py` passes. It includes the lock probe inside the model call, which acquires the checkout lock rather than raising `LockHeld`, and the existing approve, snag, refusal and provisional cases still pass. The probe also shows that `orphans` leaves out the reviewed stem, which keeps its state.
2. `./dev.py test tests/integration/test_journal.py tests/integration/test_journal_roll.py` passes. It includes the two-process append test, which reads exactly 400 events, not fewer and not a `JournalCorruption`.
3. `./dev.py test tests/integration/test_lockfile.py tests/integration/test_drain.py` passes unchanged, and `./dev.py test tests/integration/test_reconcile.py` passes with the review-slot case.

## Verification
```
./dev.py test tests/integration/test_review_command.py tests/integration/test_journal.py tests/integration/test_journal_roll.py tests/integration/test_lockfile.py tests/integration/test_drain.py tests/integration/test_storm_producer.py tests/integration/test_reconcile.py
```

## Definition of rejected
Reject the branch if `review` holds the checkout lock during any provider call, if any `Journal.append` path writes without holding `journal.lock`, if the checkout lock is replaced or made per-ticket, or if `confirm`, `reject`, drain or serve change how they take the checkout lock.

## Time budget
- expected: 45m
- stuck: 120m

