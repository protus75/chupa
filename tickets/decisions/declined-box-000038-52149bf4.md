---
id: declined-box-000038-52149bf4
kind: declined
link: box-000038-52149bf4
reopen_after_days: 90
---
When a gate raises during `lint_gate` in `chupa/gates.py`, the exception propagates to the caller as a traceback. It is not turned into a lint problem with a paved road. The note proposes catching the exception and reporting which sample the gate raised on, once gate-lint has a CLI caller.

No runtime path calls `lint_gate`. Its only callers are tests (`tests/test_gates.py` and `tests/test_requisition.py`), so no operator or pipeline stage can see the traceback. Letting the exception propagate also fails closed, as the note itself says. The request is about future ergonomics, not a current harmful gap.

- Searching *.py for `lint_gate` finds only its definition at chupa/gates.py:117 and test call sites in tests/test_gates.py and tests/test_requisition.py
- There is no CLI or engine-stage caller of `lint_gate`
- The note's proposal depends on gate-lint getting a CLI caller, which has not happened

Message: box-000038-52149bf4
