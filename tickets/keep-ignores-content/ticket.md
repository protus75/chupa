---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/runner.py::verdict_locked
- tests/integration/test_control_cli.py::test_live_verdict_recovery_and_refusal
- tests/integration/test_control_cli.py::test_yes_matches_typed_verdict
- docs/how-chupa-works.md#6.6 The Reject queue, keep and kill

## Goal / Why
`confirm <stem>` refuses to keep a Reject-queue stem when the operator's previous keep carried the same committed `ticket.md` blob: `<stem> was already kept at this ticket content; edit the ticket before re-enqueueing`. The refusal was meant to stop an automated loop from refilling caps forever on an unchanged ticket. It blocks the person instead. Machine keeps never reset caps and never pass through `confirm`, and a person must answer `y` at a terminal (or pass `--yes`) to keep, so the refusal bounds nothing automated.

It also misreads what changed. `core-drift-preflight` attempt 4 (2026-11-08) failed `premise_failed` on a pytest name collision that `tests-package-init` fixed on main 20 minutes later. The ticket text was right and needed no edit, yet a second keep was refused until the operator edited it. The input that changed was main, not the ticket.

After this change, `confirm` keeps any stem in the Reject queue, whatever the ticket content and however many prior operator keeps exist.

## Scope in / Scope out
- In: `chupa/runner.py` `verdict_locked`. Delete the `prior_keep` lookup and its `already kept at this ticket content` refusal. The keep signal still records `ticket_sha`. The `neither a draft nor in the Reject queue` refusal is unchanged, so confirming a stem that is not awaiting a verdict still exits 2.
- In: `tests/integration/test_control_cli.py`.
  - `test_live_verdict_recovery_and_refusal` (`keep` case): the second `confirm` after a keep now reports `is neither a draft nor in the Reject queue` (the stem left the queue), not `already kept at this ticket content`; the single-`reject_verdict` count assertion stays.
  - New test, built like `test_yes_matches_typed_verdict`: ready one stem, route it to the Reject queue, `confirm` it, route it to the Reject queue again with `ticket.md` unchanged, and `confirm` again. Both exit 0 and the journal holds two `reject_verdict` `keep` `operator` signals with the same `ticket_sha`, not one.
- In: `docs/how-chupa-works.md` section 6.6: replace "A second keep at the same ticket content is refused: edit the ticket first." with a sentence saying a keep needs no ticket edit.
- Out: machine keeps, cap folds, the `ticket_changed` hold, premise parks, `reject`, the terminal prompt and `--yes`, and the VS Code extension.

## Scope fence
- chupa/runner.py
- tests/integration/test_control_cli.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_control_cli.py` passes, including the new test in which a second `confirm` at unchanged ticket content exits 0 and journals a second operator keep, not exit 2.
2. `grep -rn "already kept at this ticket content" chupa tests` prints nothing.
3. `docs/how-chupa-works.md` section 6.6 no longer says a second keep at the same content is refused.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/integration/test_control_cli.py
./dev.py test
```

## Definition of rejected
`confirm` still refuses a Reject-queue stem because of unchanged ticket content, a machine keep starts resetting caps, or `confirm` starts keeping a stem that is not in the Reject queue.

## Time budget
- expected: 20m
- stuck: 60m
