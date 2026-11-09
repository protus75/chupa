---
id: tombstone-box-000279-a929595c
kind: tombstone
link: providers-dormancy-fixture-ticket
reopen_after_days: 30
---
The provider-dormancy test (`test_cli_failure_classifier_is_dormant`) dispatched a bare `object()` as its ticket. The production dispatch path reads `ticket.stem`, so the test raised `AttributeError` and the full suite on base d7aee8f6 was red. The merged ticket `providers-dormancy-fixture-ticket` changed the fixture to dispatch a real `Ticket`.

This message describes the same defect as merged ticket `providers-dormancy-fixture-ticket`, which was scoped to replace the `object()` dispatch with a validated `Ticket`. That fix is now on main: no test file defining `test_cli_failure_classifier_is_dormant` still passes `object()`.

- tickets/providers-dormancy-fixture-ticket/ticket.md Goal: the fixture dispatches a bare `object()`, and the dispatch callback reads `ticket.stem`, raising AttributeError
- providers-dormancy-fixture-ticket is in the merged stems list
- grep on current main: no file under tests/ that holds test_cli_failure_classifier_is_dormant contains `object()`

Message: box-000279-a929595c
