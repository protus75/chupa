# Review: snag

The attempts count, defaults, routing and drain report are correct, but `runner.drive` adds an attempts pre-flight the ticket explicitly forbids, and `docs/how-chupa-works.md` section 6.1 still states the old failure sequence.

## Findings

- [scope] chupa/runner.py:151 The ticket says "Add no separate attempts check in any caller, `_admit`, or the scheduler" and that "routing at the terminal is what stops a spent stem". This new block at the top of `drive` is a separate attempts check in a caller. It tests `spent(...) == "attempts"` before any stage runs and adds a new behavior: it journals a synthetic `abandoned` terminal with `routed: reject_queue` for a run that never attempted anything. That terminal replaces the stem's real failed terminal as its latest Reject-queue entry. This is the `_admit` refusal from the earlier attempt moved one call down, not the routing the ticket specified. (do instead: Delete the pre-flight block and rely on `failure_terminal` routing the failure that reaches the cap, with the existing `drain._select` and scheduler holds stopping the stem afterward. Remove `test_attempts_cap_spent_daemon_dispatch_returns_a_routed_terminal`, which pins this path. If stems already over the limit with no routed terminal need handling, file that in the Suggestion Box as a separate ticket.)
- [acceptance] docs/how-chupa-works.md:- Section 6.1 still says that after any other non-ok terminal `runner.drive` does, in order: "4. `infra_error` / `timeout` draw the `infra` cap; `premise_failed` draws `premise_bounce`." and "5. **Diagnosis** (section 6.3), unless the outcome is `budget_exceeded` or an over-bound render." and "6. **Rework** if diagnosis said `split`, or the render was over bound". The diff's new branch at `chupa/runner.py:198` skips all of these when the failure reaches `caps.attempts`: no cap draw, no spec-gap hold, no Diagnosis and no Rework, including for an over-bound render. Section 6.4's new text describes the skipped model calls, but 6.1's ordered list is left stating the old sequence, and the `infra` and `premise_bounce` draw skip is documented nowhere. (do instead: Add a step to the section 6.1 list after the drought or quota step: a failure that reaches `caps.attempts` goes straight to the terminal, routed to the Reject queue with reason `attempts cap spent`, skipping the cap draw, spec-gap hold, Diagnosis and Rework steps.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "be1bd0a6f0f1d28372b744f245bf86dbaada0909",
  "stem": "attempts-cap",
  "reviewed_sha": "be1bd0a6f0f1d28372b744f245bf86dbaada0909",
  "summary": "The attempts count, defaults, routing and drain report are correct, but `runner.drive` adds an attempts pre-flight the ticket explicitly forbids, and `docs/how-chupa-works.md` section 6.1 still states the old failure sequence.",
  "findings": [
    {
      "code": "scope",
      "path": "chupa/runner.py",
      "line": 151,
      "message": "The ticket says \"Add no separate attempts check in any caller, `_admit`, or the scheduler\" and that \"routing at the terminal is what stops a spent stem\". This new block at the top of `drive` is a separate attempts check in a caller. It tests `spent(...) == \"attempts\"` before any stage runs and adds a new behavior: it journals a synthetic `abandoned` terminal with `routed: reject_queue` for a run that never attempted anything. That terminal replaces the stem's real failed terminal as its latest Reject-queue entry. This is the `_admit` refusal from the earlier attempt moved one call down, not the routing the ticket specified.",
      "paved_road": "Delete the pre-flight block and rely on `failure_terminal` routing the failure that reaches the cap, with the existing `drain._select` and scheduler holds stopping the stem afterward. Remove `test_attempts_cap_spent_daemon_dispatch_returns_a_routed_terminal`, which pins this path. If stems already over the limit with no routed terminal need handling, file that in the Suggestion Box as a separate ticket.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "Section 6.1 still says that after any other non-ok terminal `runner.drive` does, in order: \"4. `infra_error` / `timeout` draw the `infra` cap; `premise_failed` draws `premise_bounce`.\" and \"5. **Diagnosis** (section 6.3), unless the outcome is `budget_exceeded` or an over-bound render.\" and \"6. **Rework** if diagnosis said `split`, or the render was over bound\". The diff's new branch at `chupa/runner.py:198` skips all of these when the failure reaches `caps.attempts`: no cap draw, no spec-gap hold, no Diagnosis and no Rework, including for an over-bound render. Section 6.4's new text describes the skipped model calls, but 6.1's ordered list is left stating the old sequence, and the `infra` and `premise_bounce` draw skip is documented nowhere.",
      "paved_road": "Add a step to the section 6.1 list after the drought or quota step: a failure that reaches `caps.attempts` goes straight to the terminal, routed to the Reject queue with reason `attempts cap spent`, skipping the cap draw, spec-gap hold, Diagnosis and Rework steps.",
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
