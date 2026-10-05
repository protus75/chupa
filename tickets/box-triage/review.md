# Review: snag

The diff meets the ticket in most respects, but the crash-resume path resolves a message from a decision record that exists only in the working tree, so a message can be resolved before its record commits.

## Findings

- [logic] chupa/triage.py:82 `read_registry` globs `tickets/decisions/*.md` in the working tree and does not check HEAD. Suppose a pass crashes, or `git commit` raises, after `checkout.fs.write` has put the record on disk but before the `chupa(decisions): <id>` commit lands. On the next pass, step 1 finds the uncommitted file and calls `box.resolve`, and the record is never committed. The message ends up resolved with no ticket-plane commit. This hits the Definition of rejected ('a message is resolved before its record commits') and the ticket rule 'The message is resolved only after the commit'. Any stray untracked file named `decision-<id>.md` would resolve a message the same way. The tombstone-link check at the `any(r.id == link for r, _ in registry)` branch has the same flaw: an uncommitted record counts as a valid target. (do instead: Before resolving from an existing record, confirm it is committed with `checkout.git.rev_parse(checkout.repo, f"HEAD:{record_path(id)}")`. If the file is on disk but not committed, run the same `driver.effects.run` commit (key `ticket-plane/decisions/<id>`, staging that path only) and resolve the message after that. Check tombstone-link registry targets against HEAD in the same way. Add a test where the record file exists but is uncommitted: the pass must commit it before the message is resolved.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "eef7e9793f29e3643e28b0684a2b34cf314cc2d8",
  "stem": "box-triage",
  "reviewed_sha": "eef7e9793f29e3643e28b0684a2b34cf314cc2d8",
  "summary": "The diff meets the ticket in most respects, but the crash-resume path resolves a message from a decision record that exists only in the working tree, so a message can be resolved before its record commits.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/triage.py",
      "line": 82,
      "message": "`read_registry` globs `tickets/decisions/*.md` in the working tree and does not check HEAD. Suppose a pass crashes, or `git commit` raises, after `checkout.fs.write` has put the record on disk but before the `chupa(decisions): <id>` commit lands. On the next pass, step 1 finds the uncommitted file and calls `box.resolve`, and the record is never committed. The message ends up resolved with no ticket-plane commit. This hits the Definition of rejected ('a message is resolved before its record commits') and the ticket rule 'The message is resolved only after the commit'. Any stray untracked file named `decision-<id>.md` would resolve a message the same way. The tombstone-link check at the `any(r.id == link for r, _ in registry)` branch has the same flaw: an uncommitted record counts as a valid target.",
      "paved_road": "Before resolving from an existing record, confirm it is committed with `checkout.git.rev_parse(checkout.repo, f\"HEAD:{record_path(id)}\")`. If the file is on disk but not committed, run the same `driver.effects.run` commit (key `ticket-plane/decisions/<id>`, staging that path only) and resolve the message after that. Check tombstone-link registry targets against HEAD in the same way. Add a test where the record file exists but is uncommitted: the pass must commit it before the message is resolved."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
