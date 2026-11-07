---
id: decision-box-000043-00e6ca15
kind: decision
link: box-000043-00e6ca15
reopen_after_days: 60
---
A bootstrap note says a soft gate failure comes back only as findings on an `ok` stage result, and that sending those findings to the Suggestion Box (plan invariant 3) was left for Phase 2. The box has shipped since then, and soft findings are still not sent to it. Later plan text chose this on purpose: a soft failure is reported in `checks.json` and on the stage result, and nothing is queued to the box.

There is no current harmful behavior gap. The settled design keeps soft failures out of the box. CHUPA_PLAN.md:2692 says a soft failure is reported 'without blocking and without a Suggestion Box' entry, and CHUPA_PLAN.md:2730 says 'nothing is enqueued to the Suggestion Box'. Every engine gate code is hard by default, so a soft finding exists only when an operator sets a severity override or a ticket uses `gate_bypass`. Even then the finding still appears in `checks.json` and on the stage result, so nothing is lost silently. Adding box emission now would be speculative accretion that goes against the current design.

- chupa/driver.py:387 sets tally.findings = gated.findings (soft only) on the ok path
- chupa/merge.py:309-310 returns soft findings on an ok StageResult
- chupa/stages.py:1439 returns gate and host-check findings on the check StageResult
- runner.py sends findings to the box/outbox only on failure paths (harvest_failure, failure_terminal), never for soft findings on ok
- CHUPA_PLAN.md:2692 and :2730: soft failures are reported in checks.json and on the stage result, with no Suggestion Box entry
- chupa/gates.py: every code in ENGINE_GATE_CODES is hard by default; a gate becomes soft only through a config override or the gate_bypass valve

Message: box-000043-00e6ca15
