---
id: declined-box-000178-208a05fe
kind: declined
link: box-000178-208a05fe
reopen_after_days: 90
---
A bootstrap handoff note says the merged `escalation-ladder` ticket adds `reason` (sorted finding codes, or the terminal name if there are none) and `dispatch` to the terminal `state_transition` body, and uses them as the comparison key for section 11.4. Frozen-plan unit 19.P2 calls the terminal reason "a stable code-only value" but never names the field. The note asks section 6 of the plan to name the field and how it is built.

This only asks for plan wording to match code that already shipped. The note describes no wrong runtime behavior. `CHUPA_PLAN.md` is a frozen bootstrap record and is never edited. Decisions 000173 through 000177 declined the same kind of plan-wording handoff notes.

- The message says `escalation-ladder` has merged and already writes `reason` and `dispatch` in the terminal body.
- The note only asks for the field to be named in plan section 6. It reports no failure.
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.
- Decisions 000173 through 000177 declined plan-wording requests from the same batch.

Message: box-000178-208a05fe
