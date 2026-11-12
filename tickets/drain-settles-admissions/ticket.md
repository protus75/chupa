---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Runs before
- control-inbox-known-required

## Context
- chupa/drain.py::_Drain._await_controlled
- chupa/drain.py::drain
- chupa/serve.py::Serve.apply_verdict
- chupa/control.py::ControlInbox
- chupa/__main__.py::build_control
- chupa/runner.py::verdict_locked
- tests/integration/test_drain.py::pause_checkout
- tests/integration/test_drain.py::test_stop_finishes_current_ticket_and_releases_lock
- tests/regress_bug_evidence_before_dispatch.py
- docs/how-chupa-works.md#7.3 Control

## Goal / Why
The operator cannot confirm or reject a draft while `drain` runs. On 2026-11-12, with `drain` holding the writer lock (pid 4236), the operator used the extension's right-click Confirm on `watch-folds-whole-journal` and `requisition-review-changed-text-vs-unchanged` and Reject on `implement-spec-criteria-to-tests`. Each `chupa confirm|reject --extension` call printed `submitted`, and the drain journaled every request as `control_decision` `stale` with reason "name a journaled stem or an existing ticket.md", although each stem had a `ticket.md` and journal events. All three tickets stayed `state: draft` (see `evidence/drain-admission-stale.txt`).

Cause: `serve-live-verdicts` (commit 3942110b) wired live verdicts into `serve` only. `serve` sets `inbox.known` (`chupa/serve.py`, in `Serve.__init__`) and calls `inbox.settle_admissions(self.apply_verdict)` in its merge poll. `drain` builds its consumer with `build_control` (`chupa/__main__.py`), which leaves `ControlInbox.known` at its default `lambda _: False`, and never calls `settle_admissions`. So the drain's in-flight control monitor (`_Drain._await_controlled`), which consumes the inbox every 0.1 s, decides every confirm and reject stale. `docs/how-chupa-works.md` section 7.3 says "drain decides them stale", while the section 2.1 `confirm` and `reject` rows say the verdict is published to a running drain or serve.

After this change a `confirm` or `reject` published while `drain` holds the lock is applied by the drain, with the same rules and the same result as the command run with the lock free: a confirmed draft is stamped `state: confirmed` and committed, a rejected one is stamped `rejected`. It is applied while a ticket is in flight, not only between tickets, so the operator sees it within seconds. A draft confirmed mid-drain is eligible for dispatch in the same drain invocation.

## Scope in / Scope out
- In: `chupa/__main__.py` `build_control`: set the consumer's `inbox.known` to the rule `serve` uses today (a `tickets/<stem>/ticket.md` exists, or any journal event names the stem). Both `drain` and `serve` build their consumer through `build_control`, so this is the one place it is set.
- In: `chupa/serve.py`: remove the now-duplicate `self.control.inbox.known = ...` assignment. Move the body of `Serve.apply_verdict` that applies one request crash-safely (the baseline effect, the already-applied detection, the `runner.verdict_locked` call and its refusal capture) into one function in `chupa/runner.py` that both engines call. `Serve.apply_verdict` keeps only its serve-specific tail (refusal logging via its engine log and `scheduler.update` for a confirmed published stem) around that shared function. One implementation of applying an admission, no copy.
- In: `chupa/drain.py`: call `consumer.inbox.settle_admissions(...)` with the shared apply function wherever the drain consumes its inbox: in the `_Drain._await_controlled` monitor loop while a ticket runs, and in the between-ticket control checkpoint. A refused verdict (for example a settled stem) is written to the engine log with event `verdict_refused`, as `serve` does.
- In: `tests/integration/test_drain_admissions.py` (new): the drain tests named in the acceptance criteria, built on `pause_checkout` and `build_control` (the production composition), never on a hand-set `inbox.known`.
- In: `tests/regress_drain_settles_admissions.py` (new): the carried reproducer. It runs the new test module with pytest (stdout redirected to stderr, as `tests/regress_bug_evidence_before_dispatch.py` does) and prints the `regression_result` object: `pass` and exit 0 when pytest exits 0, `defect` and exit 1 when pytest exits 1, `error` and exit 2 otherwise.
- In: `docs/how-chupa-works.md`: section 7.3 says `confirm` and `reject` publish verdict requests to the running drain or serve, which applies them; drop "drain decides them stale". Keep the section 2.1 rows consistent with it.
- Out: the `ControlInbox.known` default and the constructor signature (ticket `control-inbox-known-required`), the extension, `chupa/observe.py`, the CLI's `submitted` message, `pause`/`resume`/`kill`/`stop`/`retro` handling, `run` (which reads no control requests), and replaying requests already decided stale.

## Scope fence
- chupa/__main__.py
- chupa/serve.py
- chupa/runner.py
- chupa/drain.py
- tests/integration/test_drain_admissions.py
- tests/regress_drain_settles_admissions.py
- docs/how-chupa-works.md

## Acceptance criteria
1. In `tests/integration/test_drain_admissions.py`, a drain is started on a checkout from `pause_checkout` with a dispatched ticket held in flight (dispatch awaits an event, as `test_stop_finishes_current_ticket_and_releases_lock` does) and a committed draft `dd`. `chupa confirm dd --extension` is run while the drain holds the lock. Before the in-flight ticket is released, the test observes `tickets/dd/ticket.md` with `state: confirmed`, a `draft_confirmed` signal for `dd`, and the request's `control_decision` `accepted`, not `stale`. `./dev.py test tests/integration/test_drain_admissions.py` checks it; on the base code the decision is `stale` and the draft stays `state: draft`.
2. The same module covers `chupa reject dd --extension` under a running drain: the ticket ends `state: rejected` with a `rejected` state transition journaled, not `stale`. `./dev.py test tests/integration/test_drain_admissions.py` checks it.
3. The same module checks that the draft confirmed in criterion 1 is dispatched later in the same drain invocation (the dispatch double records `dd` after the in-flight ticket is released), not left for a later drain. `./dev.py test tests/integration/test_drain_admissions.py` checks it.
4. A request for an unknown stem under a running drain is still decided `stale` with "name a journaled stem or an existing ticket.md", and a confirm of a merged stem is journaled `accepted` and then refused with a `verdict_refused` line in `engine.log`, with the ticket file unchanged. `./dev.py test tests/integration/test_drain_admissions.py` checks both, which rules out a fix that accepts every stem or applies verdicts to settled work.
5. `grep -n "inbox.known" chupa/serve.py` prints nothing, and `grep -n "inbox.known" chupa/__main__.py` prints the one assignment in `build_control`.
6. `uv run python tests/regress_drain_settles_admissions.py` prints `{"regression_result": "pass"}` and exits 0 on the branch.
7. `docs/how-chupa-works.md` section 7.3 no longer contains `drain decides them stale`.
8. `./dev.py test` exits 0, including the existing serve live-verdict tests in `tests/integration/test_control_cli.py` and `tests/integration/test_serve_dispatch.py`.

## Verification
```
./dev.py test tests/integration/test_drain_admissions.py
./dev.py test
```

## Definition of rejected
- A drain verdict is applied only between tickets, so a confirm published during an in-flight ticket waits for that ticket to finish.
- The admission-apply logic exists twice (a copy of `Serve.apply_verdict` in `chupa/drain.py`) instead of one shared function.
- `inbox.known` is set in more than one place, or the drain tests hand-set `inbox.known` instead of using `build_control`.
- Verdict rules in `runner.verdict_locked` change, or a request for an unknown stem is accepted.
- The new drain tests pass on the base code.

## Time budget
- expected: 60m
- stuck: 120m

## Regression
```
uv run python tests/regress_drain_settles_admissions.py
```
- carries: tests/regress_drain_settles_admissions.py
- carries: tests/integration/test_drain_admissions.py
