# Review: snag

On a merge-conflict handoff that is the stem's fifth failure, the attempts route still pays for a rework call and then discards its result, leaving a published split with its parent unretired in the Reject queue.

## Findings

- [logic] chupa/runner.py:294 The early attempts check is only in `drive`, after the `ConflictHandoff` return, so it never covers the merge-conflict path. With 4 failures journaled, `consume_handoff` in `chupa/daemon.py` calls `spent` without a terminal, gets None, and runs `apply_rework`. That makes a model call and can commit successors and journal a `supersedes` signal. `failure_terminal` then counts the fifth failure and sets `rework_requested, mechanical, verdict = False, False, 'abandon-human'`, which skips the `split` branch. As a result `reject_ticket` never retires the parent: it stays `confirmed`, is journaled `gate_failed` with `routed: reject_queue`, and sits in the Reject queue as 'attempts cap spent' while its successors are live and `_select` excludes it through `supersedes_maps`. A published `update` is overwritten in the same way: the ticket has been rewritten, but the stem is rejected. The ticket forbids further model calls on this route, and the new `docs/how-chupa-works.md` 6.4 text claims 'without another diagnosis or rework call', which is false for this path. No test covers it. (do instead: In `drive`, before calling `consume_handoff`, check `spent(..., terminal={'to': 'gate_failed'}) == 'attempts'`. If it is, harvest and go straight to `failure_terminal` with `handoff.findings` and `verdict='abandon-human'`, so no rework call is made. Also make the `failure_terminal` override leave `rework_requested` handling intact when `reworked` is an ok order, so a split already published (for example through the `DaemonPipeline.consume_result` handoff, which bypasses `drive`) still retires its parent. Add a test for a fifth-failure conflict handoff. If the `consume_result` path can't avoid the call inside the fence, correct the doc sentence to match.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "82748a23a88be5107b6d90cb0f3d60ffab450bad",
  "stem": "attempts-cap",
  "reviewed_sha": "82748a23a88be5107b6d90cb0f3d60ffab450bad",
  "summary": "On a merge-conflict handoff that is the stem's fifth failure, the attempts route still pays for a rework call and then discards its result, leaving a published split with its parent unretired in the Reject queue.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/runner.py",
      "line": 294,
      "message": "The early attempts check is only in `drive`, after the `ConflictHandoff` return, so it never covers the merge-conflict path. With 4 failures journaled, `consume_handoff` in `chupa/daemon.py` calls `spent` without a terminal, gets None, and runs `apply_rework`. That makes a model call and can commit successors and journal a `supersedes` signal. `failure_terminal` then counts the fifth failure and sets `rework_requested, mechanical, verdict = False, False, 'abandon-human'`, which skips the `split` branch. As a result `reject_ticket` never retires the parent: it stays `confirmed`, is journaled `gate_failed` with `routed: reject_queue`, and sits in the Reject queue as 'attempts cap spent' while its successors are live and `_select` excludes it through `supersedes_maps`. A published `update` is overwritten in the same way: the ticket has been rewritten, but the stem is rejected. The ticket forbids further model calls on this route, and the new `docs/how-chupa-works.md` 6.4 text claims 'without another diagnosis or rework call', which is false for this path. No test covers it.",
      "paved_road": "In `drive`, before calling `consume_handoff`, check `spent(..., terminal={'to': 'gate_failed'}) == 'attempts'`. If it is, harvest and go straight to `failure_terminal` with `handoff.findings` and `verdict='abandon-human'`, so no rework call is made. Also make the `failure_terminal` override leave `rework_requested` handling intact when `reworked` is an ok order, so a split already published (for example through the `DaemonPipeline.consume_result` handoff, which bypasses `drive`) still retires its parent. Add a test for a fifth-failure conflict handoff. If the `consume_result` path can't avoid the call inside the fence, correct the doc sentence to match.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.1",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
