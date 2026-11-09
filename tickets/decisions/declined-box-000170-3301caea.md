---
id: declined-box-000170-3301caea
kind: declined
link: box-000170-3301caea
reopen_after_days: 90
---
A bootstrap review note found a wording conflict in the frozen plan. Prompt 15 says budget and timeout enforcement is pinned by tests against the committed report artifact. The merged `diagnosis-eval-harness` tests instead check a report the harness writes during the test, and they forbid committing it, because `diagnosis-eval-run` commits the report. The note asks for prompt 15 to be reworded so the two agree.

The note is only about plan wording and shows no runtime behavior that is wrong. `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited, so no ticket could make the requested change. The tests already pin enforcement against the in-test report, and `diagnosis-eval-run` has merged and committed the report. Registry records 000164 through 000169 declined similar plan-text reconciliation notes from the same diagnosis-eval batch.

- Message class suggestion, origin bootstrap-ingest: it asks only to reword prompt 15 of the frozen plan
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited
- Merged stems include diagnosis-eval-harness and diagnosis-eval-run
- declined-box-000164-c54142c4, declined-box-000167-8e1c5733 and declined-box-000169-3420a15c declined similar plan-wording reconciliation notes from the diagnosis-eval batch

Message: box-000170-3301caea
