# Review: snag

The gate, the scheduler hold, the wiring and the tests do what the ticket asks, but two statements in docs/how-chupa-works.md still say every premise_failed draws the premise_bounce cap, which a requisition-stage snag no longer does.

## Findings

- [acceptance] docs/how-chupa-works.md:- The failure-dispatch steps still say "5. `infra_error` / `timeout` draw the `infra` cap; `premise_failed` draws `premise_bounce`." After this change, runner.drive journals a `premise_failed` at stage `requisition` and returns before any cap draw. The doc now states the old behavior, and it contradicts the updated premise-park bullet in section 6.7. (do instead: Change step 5 to say `premise_failed` draws `premise_bounce` except for a `requisition`-stage snag, which ends before dispatch and draws no cap (section 6.7).)
- [acceptance] docs/how-chupa-works.md:- The caps table still says "| `premise_bounce` | 1 | each `premise_failed` (not over-bound renders) |". A `requisition`-stage `premise_failed` now draws nothing, so the table is stale. (do instead: Change the row to "each `premise_failed` (not over-bound renders or `requisition` snags)".)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "8482d4ea29687aaf01fec4579496b38b6fd64f47",
  "stem": "review-before-dispatch",
  "reviewed_sha": "8482d4ea29687aaf01fec4579496b38b6fd64f47",
  "summary": "The gate, the scheduler hold, the wiring and the tests do what the ticket asks, but two statements in docs/how-chupa-works.md still say every premise_failed draws the premise_bounce cap, which a requisition-stage snag no longer does.",
  "findings": [
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "The failure-dispatch steps still say \"5. `infra_error` / `timeout` draw the `infra` cap; `premise_failed` draws `premise_bounce`.\" After this change, runner.drive journals a `premise_failed` at stage `requisition` and returns before any cap draw. The doc now states the old behavior, and it contradicts the updated premise-park bullet in section 6.7.",
      "paved_road": "Change step 5 to say `premise_failed` draws `premise_bounce` except for a `requisition`-stage snag, which ends before dispatch and draws no cap (section 6.7).",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "The caps table still says \"| `premise_bounce` | 1 | each `premise_failed` (not over-bound renders) |\". A `requisition`-stage `premise_failed` now draws nothing, so the table is stale.",
      "paved_road": "Change the row to \"each `premise_failed` (not over-bound renders or `requisition` snags)\".",
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
