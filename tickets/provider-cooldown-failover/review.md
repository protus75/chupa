# Review: snag

When every ready ticket is drought-held, the drain blocks on the provider cooldown deadline without checking its own max-runtime deadline or a kill request, so a cooldown can hold the drain open past both.

## Findings

- [logic] chupa/drain.py:282 When `pick is None` and `provider_deadlines` is non-empty, `_Drain.run` awaits `providers.wait_until(min(self.provider_deadlines))` in one uninterrupted call. That deadline can be up to `quota_window_minutes` away (60m in fixtures). During the wait the loop never compares `self.c.clock()` to `self.deadline` (drain.max_runtime_hours), so `_halt` never fires on time. It also never re-runs `before_dispatch` or `_stopping()`, so a pause or kill request is ignored until the cooldown expires. The `storm_waiting` branch right below guards against both: it checks the deadline, then sleeps briefly. Concrete case: max_runtime_hours ends 5 minutes from now, all candidates cool for 60 minutes, and the drain overruns its ceiling by about 55 minutes and cannot be killed in that window. (do instead: Bound the wait: return `self._halt(...)` when `self.c.clock() >= self.deadline`, and otherwise wait until `min(min(self.provider_deadlines), self.deadline)`. Make the wait wake on control input as well (for example, wait in short slices and re-run the loop so `before_dispatch` and `_stopping()` see a pause or kill). Add a test in tests/test_provider_cooldown_failover.py where the drain's max runtime ends before the cooldown deadline, and assert the drain halts at its own deadline.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "bb3eb4c52a56c257e95b70967b857dd98f786956",
  "stem": "provider-cooldown-failover",
  "reviewed_sha": "bb3eb4c52a56c257e95b70967b857dd98f786956",
  "summary": "When every ready ticket is drought-held, the drain blocks on the provider cooldown deadline without checking its own max-runtime deadline or a kill request, so a cooldown can hold the drain open past both.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/drain.py",
      "line": 282,
      "message": "When `pick is None` and `provider_deadlines` is non-empty, `_Drain.run` awaits `providers.wait_until(min(self.provider_deadlines))` in one uninterrupted call. That deadline can be up to `quota_window_minutes` away (60m in fixtures). During the wait the loop never compares `self.c.clock()` to `self.deadline` (drain.max_runtime_hours), so `_halt` never fires on time. It also never re-runs `before_dispatch` or `_stopping()`, so a pause or kill request is ignored until the cooldown expires. The `storm_waiting` branch right below guards against both: it checks the deadline, then sleeps briefly. Concrete case: max_runtime_hours ends 5 minutes from now, all candidates cool for 60 minutes, and the drain overruns its ceiling by about 55 minutes and cannot be killed in that window.",
      "paved_road": "Bound the wait: return `self._halt(...)` when `self.c.clock() >= self.deadline`, and otherwise wait until `min(min(self.provider_deadlines), self.deadline)`. Make the wait wake on control input as well (for example, wait in short slices and re-run the loop so `before_dispatch` and `_stopping()` see a pause or kill). Add a test in tests/test_provider_cooldown_failover.py where the drain's max runtime ends before the cooldown deadline, and assert the drain halts at its own deadline.",
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
