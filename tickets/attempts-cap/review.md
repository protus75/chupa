# Review: snag

The attempts cap and new defaults are implemented correctly, but the diff leaves docs/how-chupa-works.md section 6.7 describing a premise park that the new premise_bounce default of 1 no longer produces.

## Findings

- [acceptance] docs/how-chupa-works.md:- Stale doc statement in section 6.7: "Premise park: after `premise_failed`, the stem waits until its committed `ticket.md` changes. The re-offer draws no retry." With the new default `premise_bounce: 1`, the first `premise_failed` spends the cap. `runner.drive` then routes the stem to the Reject queue through the mechanical `premise_bounce cap spent` verdict (the diff's own change to tests/test_terminal.py pins `dispatch: reject_queue, routed: reject_queue`). `drain._select` skips a queued stem with no budget, so a `ticket.md` edit alone never releases it, and the ticket itself notes that an edit release now needs a second premise bounce. (do instead: Update the section 6.7 premise-park bullet to match: under the default `premise_bounce: 1`, the first `premise_failed` routes to the Reject queue and only an operator `confirm` releases it. The park-until-`ticket.md`-changes release, with its no-retry re-offer, applies only when a host sets `premise_bounce` above 1.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "cb843411132d7cc11923887c0a58f9973120c86c",
  "stem": "attempts-cap",
  "reviewed_sha": "cb843411132d7cc11923887c0a58f9973120c86c",
  "summary": "The attempts cap and new defaults are implemented correctly, but the diff leaves docs/how-chupa-works.md section 6.7 describing a premise park that the new premise_bounce default of 1 no longer produces.",
  "findings": [
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "Stale doc statement in section 6.7: \"Premise park: after `premise_failed`, the stem waits until its committed `ticket.md` changes. The re-offer draws no retry.\" With the new default `premise_bounce: 1`, the first `premise_failed` spends the cap. `runner.drive` then routes the stem to the Reject queue through the mechanical `premise_bounce cap spent` verdict (the diff's own change to tests/test_terminal.py pins `dispatch: reject_queue, routed: reject_queue`). `drain._select` skips a queued stem with no budget, so a `ticket.md` edit alone never releases it, and the ticket itself notes that an edit release now needs a second premise bounce.",
      "paved_road": "Update the section 6.7 premise-park bullet to match: under the default `premise_bounce: 1`, the first `premise_failed` routes to the Reject queue and only an operator `confirm` releases it. The park-until-`ticket.md`-changes release, with its no-retry re-offer, applies only when a host sets `premise_bounce` above 1.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
