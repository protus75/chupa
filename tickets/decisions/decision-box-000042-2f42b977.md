---
id: decision-box-000042-2f42b977
kind: decision
link: box-000042-2f42b977
reopen_after_days: 90
---
A bootstrap note said `LlmStage.emits` takes only one pydantic type and proposed adding a per-verdict `emits_by_verdict` map when the first branch stage (review) was built. Review and triage have since shipped using a single verdict-tagged reply type. Its validator ties each verdict to the findings that verdict allows, so branching works without a per-verdict emit type.

No current harmful behavior. The review and triage branch stages are merged and work with one `emits` model. `ReviewVerdict` has a closed `verdict` field, and its validator rejects findings that don't match that verdict. Spec frontmatter already accepts a per-verdict `emits` dict for documentation. Adding `emits_by_verdict` to the driver would be a speculative refactor with no runtime bug behind it. Reopen if a branch stage needs a reply shape that one tagged model cannot validate, for example when two verdicts need conflicting required fields that cause a bad artifact to be accepted or a valid one to be rejected.

- chupa/driver.py:44 `emits: type[BaseModel]`, validated at chupa/driver.py:359
- chupa/stages.py:1453 review stage uses `emits=ReviewVerdict`
- chupa/artifacts.py:279-291 `ReviewVerdict` has `verdict: ReviewVerdictName` plus a `_findings_match_verdict` validator
- chupa/triage.py:318 triage stage uses single `emits=TriageReply`
- chupa/specs/__init__.py:77 spec `emits` already accepts `str | dict[str, str]` (review.md and requisition_review.md use the per-verdict map)
- review-all-findings, review-approval-records, box-triage are merged

Message: box-000042-2f42b977
