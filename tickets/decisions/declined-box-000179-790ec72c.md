---
id: declined-box-000179-790ec72c
kind: declined
link: box-000179-790ec72c
reopen_after_days: 90
---
A bootstrap handoff note says the per-dependent `failure_report` that the `reject` verb emits belongs to no pipeline stage, but the section 12 engine signature recipe needs a (stem, stage, outcome) triple. The merged `reject-queue-verbs` ticket signs it with stage `depends` and outcome `rejected`. The note asks frozen-plan section 12 to state this recipe for engine producers that have no stage.

This asks to change wording in the frozen plan, and `CHUPA_PLAN.md` is never edited. The note shows no wrong runtime behavior: the merged `reject-queue-verbs` code already signs these reports with a fixed (`depends`, `rejected`) pair. Registry records 000173 through 000178 declined the same kind of request to make plan wording match merged handoff behavior.

- The message is a suggestion from bootstrap-ingest with no stage, no outcome and no failure.
- `reject-queue-verbs` is merged and already uses stage `depends` and outcome `rejected` for this signature.
- CLAUDE.md says the frozen plan is a bootstrap design record and is never edited.
- Records declined-box-000173 through declined-box-000178 declined the same plan-wording pattern.

Message: box-000179-790ec72c
