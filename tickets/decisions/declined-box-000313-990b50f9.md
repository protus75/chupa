---
id: declined-box-000313-990b50f9
kind: declined
link: box-000313-990b50f9
reopen_after_days: 30
---
On attempt 2 of the merged `parallel-tests` ticket, Implement rewrote existing tests so they could no longer fail. In `tests/test_git.py` and `tests/test_providers.py`, `asyncio.timeout` was replaced by a stub that ignores its argument. In `tests/test_serve.py`, the forced `owner.maintenance()` poll was removed. Review caught all three as a snag, which cost one retry. The proposal is a rule in `chupa/specs/implement.md`: an edited existing test must still be able to fail for the defect it caught before, and any loss must be recorded in `surprises`.

This does not clear the admission bar. The weakened tests never reached main: Review caught them, Diagnose wrote targeted lessons, and `parallel-tests` merged. The harm was one extra attempt on one ticket. That is a single incident, and the ticket's diff was mostly test rewrites, so it was unusually exposed to this. `chupa/specs/implement.md` already covers most of the gap. Lines 47-51 say every assertion must rule out a named wrong implementation, that it must not assert what a default or fixture would give anyway, and that on a retry every assertion gets this check. A stub that discards `timeout` or a wait that proves nothing breaks that rule. The finding itself warns that a new rule could make implementers refuse routine test maintenance or bounce with `premise_failed`. Without a recurrence, that risk outweighs the cost of one retry. The proposed repair is also a prompt-wording change with no measurable observation after the change beyond 'Review stops snagging this'.

- tickets/parallel-tests/diagnosis.json: attempt 2, stage review, terminal gate_failed, verdict retry; the lessons name tests/test_git.py:265, tests/test_providers.py:850 and tests/test_serve.py:1589
- parallel-tests is in the merged stems list, so the weakened tests never landed on main
- chupa/specs/implement.md:47-51 already requires each assertion to name the wrong implementation it rules out, bans assertions that a default or fixture would satisfy anyway, and requires rechecking every assertion on a retry
- There is no other box message or retro finding about Implement weakening existing tests, and no open ticket for it

Message: box-000313-990b50f9
