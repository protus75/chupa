# Review: snag

Serve's self-upgrade can hand off while a ticket is still mid-ticket: once an upgrade is pending, writer continuations are never dispatched, and the idle check doesn't count them.

## Findings

- [logic] chupa/serve.py:318 upgrade_idle() checks only scheduler.active, admission.active, admission.task and the queue's pending/active entries. It ignores TicketWriter continuations, which are tickets paused at a stage boundary (next_stage set) that have not reached a terminal. So when a ticket is parked in a continuation, for example after a ConflictHandoff or a yielded boundary, serve sees itself as idle and hands off mid-ticket. The ticket forbids this ('A handoff that spawns ... mid-ticket'). (do instead: Make upgrade_idle() also require that no writer is active or holds continuations, e.g. `not any(w.active or w.continuations for w in self.writers.values())`, and add a test where a continuation exists when the upgrade is detected.)
- [logic] chupa/serve.py:331 Once self.upgrade is set, dispatch() skips scheduler.dispatch_next() entirely. That makes the writer exemption added to select() at line 246 (`self.upgrade is None or ticket.stem in self.writers`) dead code. In-flight tickets with continuations can never resume, so they either stall serve forever or get abandoned by the handoff. (do instead: Keep calling dispatch_next() while an upgrade is pending and let select() refuse new stems (it already exempts writers), so continuing tickets run to their terminal before upgrade_idle() allows the handoff.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "30c45ffa9695a94760ea06a813654ee200374705",
  "stem": "serve-self-upgrade",
  "reviewed_sha": "30c45ffa9695a94760ea06a813654ee200374705",
  "summary": "Serve's self-upgrade can hand off while a ticket is still mid-ticket: once an upgrade is pending, writer continuations are never dispatched, and the idle check doesn't count them.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/serve.py",
      "line": 318,
      "message": "upgrade_idle() checks only scheduler.active, admission.active, admission.task and the queue's pending/active entries. It ignores TicketWriter continuations, which are tickets paused at a stage boundary (next_stage set) that have not reached a terminal. So when a ticket is parked in a continuation, for example after a ConflictHandoff or a yielded boundary, serve sees itself as idle and hands off mid-ticket. The ticket forbids this ('A handoff that spawns ... mid-ticket').",
      "paved_road": "Make upgrade_idle() also require that no writer is active or holds continuations, e.g. `not any(w.active or w.continuations for w in self.writers.values())`, and add a test where a continuation exists when the upgrade is detected.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/serve.py",
      "line": 331,
      "message": "Once self.upgrade is set, dispatch() skips scheduler.dispatch_next() entirely. That makes the writer exemption added to select() at line 246 (`self.upgrade is None or ticket.stem in self.writers`) dead code. In-flight tickets with continuations can never resume, so they either stall serve forever or get abandoned by the handoff.",
      "paved_road": "Keep calling dispatch_next() while an upgrade is pending and let select() refuse new stems (it already exempts writers), so continuing tickets run to their terminal before upgrade_idle() allows the handoff.",
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
