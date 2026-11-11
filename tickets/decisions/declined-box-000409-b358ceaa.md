---
id: declined-box-000409-b358ceaa
kind: declined
link: box-000409-b358ceaa
reopen_after_days: 14
---
The suggestion asks `chupa lint` to reject a `kind: bug` ticket whose `## Regression` command is a plain test runner (`./dev.py test`, pytest) and not a reproducer that prints the regression JSON result. Today only requisition review catches this, so drain-ceiling-carried-on-handoff and reoffer-infra-no-retry-draw both reached review with bare `./dev.py test` regressions. The confirmed ticket `lint-requisition-decidable-rules` already adds this exact lint rule.

The confirmed ticket `tickets/lint-requisition-decidable-rules/ticket.md` sits in the working tree but intake has not committed it yet, which is why it is missing from the open-ticket list. In `validate_ticket` it adds a rule that the `## Regression` command must run a path under one of its `carries:` prefixes. Its paved road says a test runner such as `./dev.py test` or pytest does not speak the regression protocol. The rule runs at intake, in `chupa lint` and in `chupa new`, before any model call. Its acceptance criterion 1 tests the exact case in this suggestion: `./dev.py test tests/x.py` gets a finding and a carried reproducer gets none. Its Goal cites the same incidents (retro/30 and retro/35, drain-ceiling-carried-on-handoff). The suggestion asks for the same change in different words. Reopen if `lint-requisition-decidable-rules` is rejected or abandoned without merging, or if it merges and a bug ticket with a bare runner Regression command still passes `chupa lint`.

- tickets/lint-requisition-decidable-rules/ticket.md:26 names Regression running `./dev.py test` or pytest instead of a carried reproducer as a miss in retro/30 and retro/35 (drain-ceiling-carried-on-handoff)
- tickets/lint-requisition-decidable-rules/ticket.md:36 adds the 'Regression runs a carried file' rule to validate_ticket, as an allowlist with no list of banned runners
- tickets/lint-requisition-decidable-rules/ticket.md:61 acceptance criterion: `./dev.py test tests/x.py` with `carries: tests/regress_x.py` gets the finding
- chupa/tickets.py:484-500 `_regression` checks today only for a single command and test/fixture `carries:` prefixes, not whether the command runs a carried file
- merged requisition-review-regression-protocol-snag catches this only at requisition review, a model call
- unresolvable link: lint-requisition-decidable-rules

Message: box-000409-b358ceaa
