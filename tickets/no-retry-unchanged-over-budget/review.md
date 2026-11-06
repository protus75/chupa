# Review: snag

The hold and its tests match the ticket, but the new _settle diff_budget road ignores spent caps, so it can point to a ticket.md edit that cannot release the stem.

## Findings

- [logic] chupa/drain.py:617 The diff_budget road branch has no `spent_cap is None` guard, unlike the premise-park branch it sits beside. When a stem fails with diff_budget and its retry or attempts cap is spent, the parked report still says to commit the `ticket.md` change. The cap-spent road says the opposite: 'a `ticket.md` edit never re-arms the cap'. The operator is sent to a release that cannot work. (do instead: Add `and spent_cap is None` to the diff_budget condition at line 617 and to the matching awaiting guard at line 633. A cap-spent diff_budget stem then gets the cap-spent road and wording, while an uncapped budget park keeps the diff-budget road.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "93374c1f439c8c90f22894183b32160b82ef901b",
  "stem": "no-retry-unchanged-over-budget",
  "reviewed_sha": "93374c1f439c8c90f22894183b32160b82ef901b",
  "summary": "The hold and its tests match the ticket, but the new _settle diff_budget road ignores spent caps, so it can point to a ticket.md edit that cannot release the stem.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/drain.py",
      "line": 617,
      "message": "The diff_budget road branch has no `spent_cap is None` guard, unlike the premise-park branch it sits beside. When a stem fails with diff_budget and its retry or attempts cap is spent, the parked report still says to commit the `ticket.md` change. The cap-spent road says the opposite: 'a `ticket.md` edit never re-arms the cap'. The operator is sent to a release that cannot work.",
      "paved_road": "Add `and spent_cap is None` to the diff_budget condition at line 617 and to the matching awaiting guard at line 633. A cap-spent diff_budget stem then gets the cap-spent road and wording, while an uncapped budget park keeps the diff-budget road.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
