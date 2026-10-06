# Review: snag

The test fixture passes only because of a workaround in chupa/driver.py's race(): the driver re-reads the clock once, right after the call starts, while the stuck-budget timer still runs on real wall-clock asyncio.sleep, so the fixture proves nothing about the stuck-budget kill.

## Findings

- [logic] chupa/driver.py:250 The added block in race() re-reads self.clock() once, after the call's first step, and kills the call only if the clock has already passed the budget at that moment. If the injected clock moves forward later in the hang, nothing sees it: the timer is still `self.sleep(remaining)`, and the runner wires that to raw `asyncio.sleep` (chupa/runner.py:81 and :212), which means 20 real minutes. If the clock moves forward only part of the way, `remaining` is reduced, but the code then waits on the old timer with the full original duration. That contradicts its own comment ('rather than waiting for the stale timer'). The comment's justification (a seam-backed clock moving forward at the first await 'as it does when a subprocess reports elapsed time') matches no seam in the repo. The only reason this path fires is that the fixture's `advance_then_hang` moves the clock forward inside the script callable before it returns HANG. So stuck_budget_kill's observable comes from a production branch built for the fixture, not from the stuck-budget mechanism the ticket asks to pin. (do instead: Revert the race() addition. The real defect is that the stuck-budget timer is not driven by the injectable clock/sleep seam: the runner passes raw asyncio.sleep, and Checkout has no sleep seam. That fix belongs in chupa/runner.py and the Checkout seams, which are outside this ticket's fence. File it as a second problem in the Suggestion Box and reply `premise_failed`, naming it, as the ticket's Owners clause requires. Alternatively, if the fix can stay entirely inside chupa/driver.py, make race() honour the clock seam for the whole wait (for example, a timer that sleeps through the Sleep seam and re-checks deadline against self.clock() each time it wakes). Then make the fixture move the clock forward during the hang, not before it starts.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "e586aaba090cf3343d4c7bca294dc6451de2f884",
  "stem": "shakeout-driver",
  "reviewed_sha": "e586aaba090cf3343d4c7bca294dc6451de2f884",
  "summary": "The test fixture passes only because of a workaround in chupa/driver.py's race(): the driver re-reads the clock once, right after the call starts, while the stuck-budget timer still runs on real wall-clock asyncio.sleep, so the fixture proves nothing about the stuck-budget kill.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/driver.py",
      "line": 250,
      "message": "The added block in race() re-reads self.clock() once, after the call's first step, and kills the call only if the clock has already passed the budget at that moment. If the injected clock moves forward later in the hang, nothing sees it: the timer is still `self.sleep(remaining)`, and the runner wires that to raw `asyncio.sleep` (chupa/runner.py:81 and :212), which means 20 real minutes. If the clock moves forward only part of the way, `remaining` is reduced, but the code then waits on the old timer with the full original duration. That contradicts its own comment ('rather than waiting for the stale timer'). The comment's justification (a seam-backed clock moving forward at the first await 'as it does when a subprocess reports elapsed time') matches no seam in the repo. The only reason this path fires is that the fixture's `advance_then_hang` moves the clock forward inside the script callable before it returns HANG. So stuck_budget_kill's observable comes from a production branch built for the fixture, not from the stuck-budget mechanism the ticket asks to pin.",
      "paved_road": "Revert the race() addition. The real defect is that the stuck-budget timer is not driven by the injectable clock/sleep seam: the runner passes raw asyncio.sleep, and Checkout has no sleep seam. That fix belongs in chupa/runner.py and the Checkout seams, which are outside this ticket's fence. File it as a second problem in the Suggestion Box and reply `premise_failed`, naming it, as the ticket's Owners clause requires. Alternatively, if the fix can stay entirely inside chupa/driver.py, make race() honour the clock seam for the whole wait (for example, a timer that sleeps through the Sleep seam and re-checks deadline against self.clock() each time it wakes). Then make the fixture move the clock forward during the hang, not before it starts."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
