---
id: tombstone-box-000214-963a4a6c
kind: tombstone
link: declined-box-000042-2f42b977
reopen_after_days: 90
---
A bootstrap note says `LlmStage.emits` accepts a single pydantic reply type and asks for a per-verdict `emits_by_verdict` map when the first branch stage (review or triage) is built. Registry record 000042 already settled this same request.

This message makes the same request as registry record declined-box-000042-2f42b977. That record found that review and triage shipped with one verdict-tagged reply type, and that type's validator ties each verdict to the findings it allows. Branch stages therefore work without a per-verdict emit type. The message adds no new evidence and reports no harmful runtime behavior.

- Registry record declined-box-000042-2f42b977 covers the same `LlmStage.emits` / `emits_by_verdict` proposal for branch stages
- Merged stems include `review-all-findings`, `box-triage` and `review-reprompt-invalid-reply`, so branch stages already run on a single reply type

Message: box-000214-963a4a6c
