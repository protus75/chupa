---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- drain-settles-admissions

## Context
- chupa/control.py::ControlInbox
- chupa/daemon.py::control_inbox
- chupa/daemon.py::PauseConsumer
- chupa/__main__.py::build_control
- chupa/serve.py::Serve

## On-demand
- tests/integration/test_control_cli.py
- tests/integration/test_control.py
- tests/integration/test_kill_signal_journal.py
- tests/integration/test_kill_cli_activation.py
- tests/integration/test_daemon_composition.py
- tests/integration/test_mergequeue.py

## Goal / Why
`ControlInbox.__init__` sets `self.known = lambda _: False`, and an owner wires the real rule by assigning the attribute after construction. An owner that forgets the assignment decides every `confirm` and `reject` request `stale` with no error at construction and no failing test. That is how `drain` silently dropped every operator verdict on 2026-11-12 (ticket `drain-settles-admissions`): `serve-live-verdicts` assigned `inbox.known` in `serve` only, and tests in `tests/integration/test_control_cli.py` that take a `drain` lock assign `inbox.known` by hand, so they passed while the production drain composition stayed broken. The default is a fail-stuck hold with no release.

After this change no inbox can exist without a stem rule: `known` is a required keyword-only constructor parameter with no default, passed through `daemon.control_inbox` and `daemon.PauseConsumer`, and supplied once by `build_control`. Nothing assigns `inbox.known` after construction, so a new engine verb or a refactor that omits the rule fails with `TypeError` at construction instead of silently staling verdicts.

## Scope in / Scope out
- In: `chupa/control.py`: `ControlInbox.__init__` takes required keyword-only `known: Callable[[str], bool]`; remove the `lambda _: False` default.
- In: `chupa/daemon.py`: `control_inbox` and `PauseConsumer.__init__` take required keyword-only `known` and pass it through.
- In: `chupa/__main__.py` `build_control`: the one `consumer.inbox.known = ...` assignment (added by `drain-settles-admissions`) becomes the `known=` constructor argument to `PauseConsumer`. `chupa/serve.py` has no `inbox.known` assignment after `drain-settles-admissions`; leave it so.
- In: the integration tests that construct `ControlInbox`, `control_inbox` or `PauseConsumer` pass `known` explicitly, and the tests that assign `inbox.known` after construction pass it to the constructor instead: `tests/integration/test_control_cli.py`, `tests/integration/test_control.py`, `tests/integration/test_kill_signal_journal.py`, `tests/integration/test_kill_cli_activation.py`, `tests/integration/test_daemon_composition.py`, `tests/integration/test_mergequeue.py`.
- In: `tests/unit/test_control_known.py` (new): the constructor tests in the acceptance criteria.
- Out: the stem rule itself, admission settling in drain or serve, `tests/unit/test_verdict_extension.py` (it builds the inbox with `object.__new__` and never calls `__init__`), every other control verb.

## Scope fence
- chupa/control.py
- chupa/daemon.py
- chupa/__main__.py
- chupa/serve.py
- tests/unit/test_control_known.py
- tests/integration/test_control_cli.py
- tests/integration/test_control.py
- tests/integration/test_kill_signal_journal.py
- tests/integration/test_kill_cli_activation.py
- tests/integration/test_daemon_composition.py
- tests/integration/test_mergequeue.py

## Acceptance criteria
1. `tests/unit/test_control_known.py` asserts that constructing `ControlInbox` without `known` raises `TypeError`, not an inbox whose `known` returns `False`; checked by `./dev.py test tests/unit/test_control_known.py`.
2. The same module asserts that `daemon.PauseConsumer` constructed without `known` raises `TypeError`, and that a `PauseConsumer` constructed with `known=lambda s: s == "x"` has `inbox.known("x")` true and `inbox.known("y")` false; checked by `./dev.py test tests/unit/test_control_known.py`.
3. `grep -rnE "inbox\.known *=" chupa tests` prints nothing, which rules out an owner or test that still wires the rule after construction.
4. `grep -n "lambda _: False" chupa/control.py` prints nothing.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/unit/test_control_known.py
./dev.py test
```

## Definition of rejected
- `known` keeps any default value, or a factory or wrapper supplies one so that an omitted rule does not fail at construction.
- The stem rule `build_control` supplies changes (which stems are accepted).
- Any engine verb's admission settling behavior changes.

## Time budget
- expected: 30m
- stuck: 75m
