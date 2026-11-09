---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: draft
---

## Depends on
- none

## Context
- chupa/__main__.py::_verdict
- chupa/drain.py::reofferable
- chupa/drain.py::awaiting_operator
- tests/integration/test_reject_queue.py
- tests/unit/test_verdict_extension.py

## Goal / Why
`chupa confirm <stem>` on a Reject-queue stem prints `Reject queue: <to> -- <reason>` and asks y/N, whether or not the drain would re-offer that stem anyway. `drain.reofferable` is true for a queued stem that is not awaiting the operator, such as a `premise_failed` stem with `premise_bounce` budget left. The drain re-offers it with no keep. An operator who answers y journals `reject_verdict keep actor: operator`, and `caps.lineage` then restarts every cap count after it. The confirm bypasses the bounded retry and attempt budget the caps exist to enforce, and the prompt gives no hint of this. After this change, when the verb is `confirm`, the stem is in the Reject queue, and `drain.reofferable` is true, the preview adds a second line saying the drain re-offers this stem without a keep and that a keep resets its cap budget. A cap-spent or ticket_changed stem, and the `reject` verb, print no such line.

## Scope in / Scope out
- In: `chupa/__main__.py` `_verdict`: one branch that prints the note when `verb == "confirm"`, `queued is not None` and `drain.reofferable(history, stem, checkout.config.caps)`.
- In: `tests/integration/test_reject_queue.py`: one test that runs confirm on a queued re-offerable stem and one on a queued cap-spent stem and compares the two prompts.
- In: `tests/unit/test_verdict_extension.py`: a unit test that drives `entry._verdict` with that file's fake Journal and a SimpleNamespace checkout whose `config.caps` is set, so the new branch is covered by the unit suite that enforces the per-file coverage floor for `chupa/__main__.py`. It asserts the note prints for `confirm` on a queued stem with budget left, and does not print for a cap-spent stem or for the `reject` verb.
- Out: the `reject` verb behavior, the extension, `docs/`, the keep semantics, and any change to `drain.py` or `caps.py`.
- Rejected simpler approach: none. Rewording the existing preview alone cannot tell the two cases apart, so the `reofferable` check is the minimum.

## Scope fence
- chupa/__main__.py
- tests/integration/test_reject_queue.py
- tests/unit/test_verdict_extension.py

## Acceptance criteria
1. For a queued stem with cap budget left, `./dev.py test tests/integration/test_reject_queue.py` asserts the confirm output contains `re-offers this stem without a keep`, which rules out a prompt that is unchanged for re-offerable stems.
2. For a queued stem whose retry cap is spent, the same test file asserts the confirm output does not contain `re-offers this stem without a keep`, which rules out a note printed for every queued stem.
3. The same test file asserts the `reject` verb on a re-offerable queued stem does not print `re-offers this stem without a keep`, which rules out a note shown on the kill verb.
4. The existing `test_verdict_requires_yes` still asserts `held: Reject queue:` in the output, which rules out a change that drops the first preview line.
5. `./dev.py test tests/unit/test_verdict_extension.py` runs a unit test that calls `entry._verdict` for `confirm` on a queued stem with budget left and asserts the output contains `re-offers this stem without a keep`, and for a cap-spent stem and for the `reject` verb asserts it does not, which rules out a branch that is untested by the unit suite or printed for every queued stem.

## Verification
```
./dev.py test tests/integration/test_reject_queue.py
./dev.py test tests/unit/test_verdict_extension.py
```

## Definition of rejected
The note appears for cap-spent or ticket_changed stems; the note appears on `reject`; the first preview line changes; the answer handling or keep behavior changes; the new branch has no unit test; any file outside `## Scope fence` changes.

## Time budget
- expected: 25m
- stuck: 50m
