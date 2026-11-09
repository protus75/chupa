# Review: snag

The menu plumbing matches the ticket, but `chupaRun` adds a `not held` condition the ticket does not specify, so it changes Run availability for held tickets without being asked to.

## Findings

- [scope] chupa/observe.py:585 `chupaRun` is computed as `available(r["runnable"] and not r["held"])`. The ticket's rule is exactly "`chupaRun`: `off` unless `runnable`; then `locked` when the engine is alive, else `on`." A row's `runnable` (observe.py:549) does not exclude held stems. So a held, confirmed ticket whose dependencies are met now gets `off` where the rule gives `on` (no engine) or `locked` (engine alive). The old menu enabled Run for it (`chupaRunnable && !chupaEngine`), and `chupa run` has no held refusal that would justify the extra condition. The test's held row is confirmed with no `depends`, so it is runnable, and its `chupaRun == 'off'` assertion passes only because of this unrequested condition. (do instead: Use `available(r["runnable"])` as the ticket specifies. In `test_snapshot_menu_availability`, make the held row non-runnable (for example, give it a `depends` on a stem that has not merged) so `chupaRun` is `off` because of `runnable`. If held tickets really must not be runnable from the menu, file that as a Suggestion Box item instead of adding it here.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f1e771a27f74dd487417fa702ed0cfc343d4aa7c",
  "stem": "vscode-verdict-menu",
  "reviewed_sha": "f1e771a27f74dd487417fa702ed0cfc343d4aa7c",
  "summary": "The menu plumbing matches the ticket, but `chupaRun` adds a `not held` condition the ticket does not specify, so it changes Run availability for held tickets without being asked to.",
  "findings": [
    {
      "code": "scope",
      "path": "chupa/observe.py",
      "line": 585,
      "message": "`chupaRun` is computed as `available(r[\"runnable\"] and not r[\"held\"])`. The ticket's rule is exactly \"`chupaRun`: `off` unless `runnable`; then `locked` when the engine is alive, else `on`.\" A row's `runnable` (observe.py:549) does not exclude held stems. So a held, confirmed ticket whose dependencies are met now gets `off` where the rule gives `on` (no engine) or `locked` (engine alive). The old menu enabled Run for it (`chupaRunnable && !chupaEngine`), and `chupa run` has no held refusal that would justify the extra condition. The test's held row is confirmed with no `depends`, so it is runnable, and its `chupaRun == 'off'` assertion passes only because of this unrequested condition.",
      "paved_road": "Use `available(r[\"runnable\"])` as the ticket specifies. In `test_snapshot_menu_availability`, make the held row non-runnable (for example, give it a `depends` on a stem that has not merged) so `chupaRun` is `off` because of `runnable`. If held tickets really must not be runnable from the menu, file that as a Suggestion Box item instead of adding it here.",
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
