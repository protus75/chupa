---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- remove-merge-hold

## Context
- chupa/__main__.py
- chupa/control.py
- chupa/runner.py
- chupa/serve.py
- tests/test_control_cli.py
- tests/test_control.py
- chupa/mergequeue.py

## On-demand
- chupa/status.py
- tests/test_serve.py
- docs/how-chupa-works.md

## Goal / Why
`serve` is meant to run continuously, but today the operator must stop it to keep or kill a Reject-queue ticket, or to reject a draft. `confirm`/`reject` take the writer lock, and on `LockHeld` only a draft `confirm` falls back to the control inbox (`chupa/__main__.py` `_verdict`); every other verdict exits 2 "lock held". After this change every `confirm` and `reject` the operator can give with the lock free also works while serve holds it, so the operator never stops serve to make a decision.

## Scope in / Scope out
- In: `chupa/runner.py`: split `verdict` into the lock-taking wrapper and one lock-free function that holds every keep, kill and draft-promotion rule it has today. Both the CLI path and serve call that function, so there is one implementation of the verdict rules.
- In: `chupa/__main__.py` `_verdict`: on `LockHeld`, always publish an `AdmissionRequest` (`hold_id` null) for `confirm` and `reject`, replacing the draft-confirm-only fallback. The TTY `y` prompt is unchanged. Print `<verb> submitted: <request_id> -- ./dev.py status shows the outcome`.
- In: `chupa/control.py` and `chupa/serve.py`:
  - The inbox accepts a null-`hold_id` request when the stem is a committed draft or is in `reject_queue`, and decides it stale otherwise. The stale road is "run status; the stem is not awaiting a verdict".
  - `settle_admissions` applies each accepted request once by calling the lock-free verdict function under an `Effects` key `ticket-plane/<stem>/<verb>/<request_id>`. The key keeps a crash or a repeated pass from applying it twice.
  - A verdict the function refuses (for example "already kept at this ticket content", or a settled stem) completes its effect with the refusal message and road. It is written to the engine log, and `status` shows it.
- In: serve's dispatch re-offers a kept stem on its next scheduling pass, with no restart.
- In: `docs/how-chupa-works.md`:
  - section 2.1: in the `confirm` and `reject` rows, Lock becomes `try`, and the text says the verdict is published to a running serve;
  - section 6.6: keep and kill work while serve runs;
  - section 7.3: the inbox carries verdict requests.
- Out: drain consuming verdict requests. A request published while drain runs is decided stale as today, and section 7.3 says so. Also out: machine keep in serve, `pause`/`resume`/`kill`, and the TTY confirmation.

## Scope fence
- chupa/__main__.py
- chupa/control.py
- chupa/runner.py
- chupa/serve.py
- chupa/status.py
- tests/test_control_cli.py
- tests/test_control.py
- tests/test_serve.py
- tests/test_reject_queue.py
- docs/how-chupa-works.md

## Acceptance criteria
1. While a lock is held, `confirm <stem>` on a Reject-queue stem publishes a request. The running serve journals `reject_verdict keep actor: operator` exactly once, even when `settle_admissions` runs twice or restarts mid-effect. Checked by `uv run pytest tests/test_control.py tests/test_control_cli.py`.
2. While a lock is held, `reject <stem>` on a Reject-queue stem and on a committed draft stamps `state: rejected`, commits it, journals the `rejected` transition once, and files dead-dependent box messages exactly as the lock-free path does. Checked by `uv run pytest tests/test_control.py tests/test_control_cli.py`.
3. A kept stem dispatches on serve's next scheduling pass without a restart. Checked by `uv run pytest tests/test_serve.py`.
4. A second keep at unchanged ticket content, sent while serve runs, completes with the "already kept at this ticket content" refusal, which shows in `status`. It journals no second keep. Checked by `uv run pytest tests/test_control.py`.
5. A request for a stem that is neither a draft nor in the Reject queue is decided stale. Checked by `uv run pytest tests/test_control.py`.
6. The lock-free CLI path (no engine running) behaves exactly as before: the existing `tests/test_reject_queue.py` verdict tests pass unchanged.
7. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_control.py tests/test_control_cli.py tests/test_serve.py tests/test_reject_queue.py
uv run pytest -q
```

## Definition of rejected
Two copies of the keep/kill rules; a verdict applied twice; a verdict that skips the TTY `y`; serve needs a restart to dispatch a kept stem; `confirm`/`reject` still exit 2 "lock held" against a running serve.

## Time budget
- expected: 90m
- stuck: 180m
