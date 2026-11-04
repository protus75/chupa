# Review: snag

The hold works on the stage and merge-admission paths, but the intake and sha read added to `serve` dispatch can stop the daemon on a refused new ticket and can let an edit made just before dispatch escape the hold.

## Findings

- [logic] chupa/serve.py:121 Serve dispatch discards `intake`'s `refused` result and then runs `rev_parse main:tickets/<stem>/ticket.md`, which raises `GitError` when the stem has no committed blob. The Watcher publishes on `parse_ticket` alone, and the evidence and source claim checks run only in intake. A new `kind: bug`, `state: confirmed` ticket with no evidence file therefore parses, gets published and reaches dispatch, then intake refuses it. The `GitError` propagates through `DaemonAdmission.dispatch` and `Serve.dispatch` to `guarded`, which calls `self.stop()` and exits serve with code 1. The file is still on disk, so a restarted serve can hit the same failure. Before this diff the same dispatch journaled `running` and did not raise. `self.writers[stem]` is also left set, because the raise happens before the `try/finally` that pops it. (do instead: Do not let a refused or uncommitted stem kill the worker. Check for a committed blob before setting `self.writers` and appending `running`. If there is none, return without dispatching and leave the refusal to the existing intake reporting. Add a serve test where a parseable new bug ticket with no evidence is refused and serve keeps running.)
- [logic] chupa/serve.py:120 `await intake(...)` commits any pending edit at dispatch, and the next line records that new blob as `ticket_sha`, but `ticket` is still the object the Watcher parsed before the edit. If `ticket.md` is edited after the last `scan` and before dispatch, the run uses the old fence, criteria and verification with a sha that matches the new bytes. `ticket_changed` then never fires, so the run continues against a ticket it did not start with, and the Definition of rejected names that outcome. Without this intake call, the same uncommitted edit would differ from the committed blob and hold at the first stage. An edit committed in that window has the same problem, because the sha is read from main instead of being tied to the dispatched ticket's content. (do instead: Remove the dispatch-time intake, since `scan` already runs intake under the same admission slot. Make the recorded sha correspond to the dispatched ticket: compare the blob on main with the content `ticket` was parsed from, and if they differ, republish the fresh ticket with `scheduler.update` and return without dispatching. Add a serve test that edits the ticket after publication and before dispatch, and assert the run never proceeds on the old `Ticket` with the new sha.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5ea748d9343f3adb9b6667e609f6f415b125c38d",
  "stem": "ticket-changed-midrun",
  "reviewed_sha": "5ea748d9343f3adb9b6667e609f6f415b125c38d",
  "summary": "The hold works on the stage and merge-admission paths, but the intake and sha read added to `serve` dispatch can stop the daemon on a refused new ticket and can let an edit made just before dispatch escape the hold.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/serve.py",
      "line": 121,
      "message": "Serve dispatch discards `intake`'s `refused` result and then runs `rev_parse main:tickets/<stem>/ticket.md`, which raises `GitError` when the stem has no committed blob. The Watcher publishes on `parse_ticket` alone, and the evidence and source claim checks run only in intake. A new `kind: bug`, `state: confirmed` ticket with no evidence file therefore parses, gets published and reaches dispatch, then intake refuses it. The `GitError` propagates through `DaemonAdmission.dispatch` and `Serve.dispatch` to `guarded`, which calls `self.stop()` and exits serve with code 1. The file is still on disk, so a restarted serve can hit the same failure. Before this diff the same dispatch journaled `running` and did not raise. `self.writers[stem]` is also left set, because the raise happens before the `try/finally` that pops it.",
      "paved_road": "Do not let a refused or uncommitted stem kill the worker. Check for a committed blob before setting `self.writers` and appending `running`. If there is none, return without dispatching and leave the refusal to the existing intake reporting. Add a serve test where a parseable new bug ticket with no evidence is refused and serve keeps running.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/serve.py",
      "line": 120,
      "message": "`await intake(...)` commits any pending edit at dispatch, and the next line records that new blob as `ticket_sha`, but `ticket` is still the object the Watcher parsed before the edit. If `ticket.md` is edited after the last `scan` and before dispatch, the run uses the old fence, criteria and verification with a sha that matches the new bytes. `ticket_changed` then never fires, so the run continues against a ticket it did not start with, and the Definition of rejected names that outcome. Without this intake call, the same uncommitted edit would differ from the committed blob and hold at the first stage. An edit committed in that window has the same problem, because the sha is read from main instead of being tied to the dispatched ticket's content.",
      "paved_road": "Remove the dispatch-time intake, since `scan` already runs intake under the same admission slot. Make the recorded sha correspond to the dispatched ticket: compare the blob on main with the content `ticket` was parsed from, and if they differ, republish the fresh ticket with `scheduler.update` and return without dispatching. Add a serve test that edits the ticket after publication and before dispatch, and assert the run never proceeds on the old `Ticket` with the new sha.",
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
