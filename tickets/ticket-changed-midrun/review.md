# Review: snag

The `ticket_changed` stop and hold are correct on every path I traced, but `docs/how-chupa-works.md` section 6.1 still states the old failure-handling order, which this diff makes false.

## Findings

- [acceptance] docs/how-chupa-works.md:- Stale doc: section 6.1 says "After any other non-ok terminal, `runner.drive` does, in order" and lists "4. **Diagnosis** (section 6.3), unless the outcome is `budget_exceeded` or an over-bound render." and "5. **Rework** if diagnosis said `split`...". The diff adds an early return in `runner.drive`: after Harvest, a `ticket_changed` terminal goes straight to `failure_terminal` with no diagnosis or Rework, and is routed to the Reject queue. An outcome of `gate_failed` with `ticket_changed` is a non-ok terminal that section 6.1 still says gets diagnosed, which contradicts the new section 6.7 text. (do instead: Update the section 6.1 list to include the `ticket_changed` exit: after Harvest, it journals a `gate_failed` terminal routed to the Reject queue, removes the worktree, and skips the cap, Diagnosis and Rework steps. For example, add a step beside step 2 and point it to section 6.7.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5c7970ca41632e91bf3f7d6932b76274446052a9",
  "stem": "ticket-changed-midrun",
  "reviewed_sha": "5c7970ca41632e91bf3f7d6932b76274446052a9",
  "summary": "The `ticket_changed` stop and hold are correct on every path I traced, but `docs/how-chupa-works.md` section 6.1 still states the old failure-handling order, which this diff makes false.",
  "findings": [
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "Stale doc: section 6.1 says \"After any other non-ok terminal, `runner.drive` does, in order\" and lists \"4. **Diagnosis** (section 6.3), unless the outcome is `budget_exceeded` or an over-bound render.\" and \"5. **Rework** if diagnosis said `split`...\". The diff adds an early return in `runner.drive`: after Harvest, a `ticket_changed` terminal goes straight to `failure_terminal` with no diagnosis or Rework, and is routed to the Reject queue. An outcome of `gate_failed` with `ticket_changed` is a non-ok terminal that section 6.1 still says gets diagnosed, which contradicts the new section 6.7 text.",
      "paved_road": "Update the section 6.1 list to include the `ticket_changed` exit: after Harvest, it journals a `gate_failed` terminal routed to the Reject queue, removes the worktree, and skips the cap, Diagnosis and Rework steps. For example, add a step beside step 2 and point it to section 6.7.",
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
