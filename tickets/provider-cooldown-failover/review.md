# Review: snag

The pre-dispatch drought checks look up the implement route by the ticket's authored tier, not the escalated tier the runner actually uses, so a ticket on a retry rung can be parked by mistake, and in drain this disagrees with the scheduler's own check and loops forever.

## Findings

- [logic] chupa/drain.py:428 _Drain._dispatch calls session.drought(self.c.config, ticket.frontmatter.agent_tier, 'implement'), but _select (line 400) checks drought with caps.capability(t, events), and runner.drive implements at capability(ticket, history) (runner.py:149). Take a ticket escalated by a retry rung to a tier whose route is available, while the authored tier's route is fully cooling. _select finds no drought and picks it. _dispatch then parks it and returns. park dedups the identical record, nothing waits, and the next loop picks it again: drain spins forever without dispatching or sleeping. It also parks a ticket whose real route is healthy. (do instead: Resolve the implement tier once with caps.capability(ticket, history), the same fold _select and runner.drive use, and use it in every drought check (or reuse _select's verdict instead of re-checking in _dispatch).)
- [logic] chupa/__main__.py:77 The daemon/serve dispatch (and Serve's admission check, serve.py:170) evaluate drought with ticket.frontmatter.agent_tier. provider_holds then re-checks with the recorded route tier. An escalated ticket is parked, or held, against the wrong route, so a ticket with a healthy escalated route gets a provider_drought infra_error park. (do instead: Use caps.capability(ticket, checkout.journal.read())[0] for the implement-surface drought check here and in Serve's admission predicate.)
- [logic] chupa/runner.py:517 run_ticket's pre-dispatch drought check and drive's diagnosis-surface drought check (line 198) also use ticket.frontmatter.agent_tier rather than the capability tier this attempt runs at. They can park a ticket whose escalated route is available, or let one through whose escalated route is dry. (do instead: Derive the tier with capability(ticket, history) at these sites, the same way failure_terminal and drive already do.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "05a79c50ec11ee0cdd27f723f49c538306b7a100",
  "stem": "provider-cooldown-failover",
  "reviewed_sha": "05a79c50ec11ee0cdd27f723f49c538306b7a100",
  "summary": "The pre-dispatch drought checks look up the implement route by the ticket's authored tier, not the escalated tier the runner actually uses, so a ticket on a retry rung can be parked by mistake, and in drain this disagrees with the scheduler's own check and loops forever.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/drain.py",
      "line": 428,
      "message": "_Drain._dispatch calls session.drought(self.c.config, ticket.frontmatter.agent_tier, 'implement'), but _select (line 400) checks drought with caps.capability(t, events), and runner.drive implements at capability(ticket, history) (runner.py:149). Take a ticket escalated by a retry rung to a tier whose route is available, while the authored tier's route is fully cooling. _select finds no drought and picks it. _dispatch then parks it and returns. park dedups the identical record, nothing waits, and the next loop picks it again: drain spins forever without dispatching or sleeping. It also parks a ticket whose real route is healthy.",
      "paved_road": "Resolve the implement tier once with caps.capability(ticket, history), the same fold _select and runner.drive use, and use it in every drought check (or reuse _select's verdict instead of re-checking in _dispatch).",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/__main__.py",
      "line": 77,
      "message": "The daemon/serve dispatch (and Serve's admission check, serve.py:170) evaluate drought with ticket.frontmatter.agent_tier. provider_holds then re-checks with the recorded route tier. An escalated ticket is parked, or held, against the wrong route, so a ticket with a healthy escalated route gets a provider_drought infra_error park.",
      "paved_road": "Use caps.capability(ticket, checkout.journal.read())[0] for the implement-surface drought check here and in Serve's admission predicate.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/runner.py",
      "line": 517,
      "message": "run_ticket's pre-dispatch drought check and drive's diagnosis-surface drought check (line 198) also use ticket.frontmatter.agent_tier rather than the capability tier this attempt runs at. They can park a ticket whose escalated route is available, or let one through whose escalated route is dry.",
      "paved_road": "Derive the tier with capability(ticket, history) at these sites, the same way failure_terminal and drive already do.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
