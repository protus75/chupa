---
id: decision-box-000036-b6398d69
kind: decision
link: box-000036-b6398d69
reopen_after_days: 90
---
`run_gates` in `chupa/gates.py` treats any severity value except "hard" as soft. The note proposes matching "soft" explicitly and raising `GateContractError` on any other value, so a malformed severity map fails closed and cannot quietly soften a gate.

This is speculative hardening, and no current path reaches it. Severity is typed `Literal["hard", "soft"]` in `chupa/config.py`, and pydantic enforces that type when the config loads. Every `run_gates` caller gets its map either from validated config (`merge_severity`, `check_severity`, the driver's `self.severity`) or from a hard-coded literal (`merge.py` passes `{"post_rebase_regate": "hard"}`). No caller is shown passing an unvalidated mapping, and no incident shows a gate softened by a bad value. The proposal is sound defensively, but it fixes no runtime behavior that is wrong today.

- chupa/config.py:22 Severity = Literal["hard", "soft"]
- chupa/gates.py:113 buckets with `severity[gate.code] == "hard"` else soft
- chupa/gates.py:106-110 already raises GateContractError for a missing gate code
- run_gates callers (stages.py:1381, driver.py:366, merge.py:166/295/297, mergequeue.py:318-333) all pass config-derived or literal severity maps

Message: box-000036-b6398d69
