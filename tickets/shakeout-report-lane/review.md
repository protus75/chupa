# Review: snag

Check deletes only the top-level registered artifact before Verification, but the checks lift matches registered basenames at any depth, so an agent can write a valid report into a subdirectory of the outbox and get it onto main.

## Findings

- [logic] chupa/stages.py:780 `check` unlinks only `outbox / name` for each registered artifact. `lift_outbox` (`outbox.rglob("*")` filtered by `p.name in KNOWN_ARTIFACTS`) excludes registered basenames at any depth from non-check lifts, and lifts and validates them at any depth in the `checks` lift. Suppose Implement writes a schema-valid `tickets/<stem>/attempts/0/shakeout-report.json` or `tickets/<stem>/x/shakeout-report.json`. The implement-terminal lift leaves it in the outbox. The pre-Verification delete does not touch it. The Check lift then validates it and commits it to main in `chupa(<stem>): checks`. That breaks the rule that a stale or agent-written copy never lifts, and it is exactly the forged-report false-green that the custody rules refuse. (do instead: Make the pre-Verification purge and the lift use the same matching rule. Delete every outbox file whose basename is registered (`for p in outbox.rglob('*') if p.name in KNOWN_ARTIFACTS`), or restrict registered-artifact lifting to the exact top-level path `outbox / name` and leave nested copies out of every lift. Add a `tests/test_stages.py` case where Implement writes a valid report in a nested outbox path and assert it never reaches main.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f407c6ec84cdfb988982c12bb872b27fc713a0f2",
  "stem": "shakeout-report-lane",
  "reviewed_sha": "f407c6ec84cdfb988982c12bb872b27fc713a0f2",
  "summary": "Check deletes only the top-level registered artifact before Verification, but the checks lift matches registered basenames at any depth, so an agent can write a valid report into a subdirectory of the outbox and get it onto main.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/stages.py",
      "line": 780,
      "message": "`check` unlinks only `outbox / name` for each registered artifact. `lift_outbox` (`outbox.rglob(\"*\")` filtered by `p.name in KNOWN_ARTIFACTS`) excludes registered basenames at any depth from non-check lifts, and lifts and validates them at any depth in the `checks` lift. Suppose Implement writes a schema-valid `tickets/<stem>/attempts/0/shakeout-report.json` or `tickets/<stem>/x/shakeout-report.json`. The implement-terminal lift leaves it in the outbox. The pre-Verification delete does not touch it. The Check lift then validates it and commits it to main in `chupa(<stem>): checks`. That breaks the rule that a stale or agent-written copy never lifts, and it is exactly the forged-report false-green that the custody rules refuse.",
      "paved_road": "Make the pre-Verification purge and the lift use the same matching rule. Delete every outbox file whose basename is registered (`for p in outbox.rglob('*') if p.name in KNOWN_ARTIFACTS`), or restrict registered-artifact lifting to the exact top-level path `outbox / name` and leave nested copies out of every lift. Add a `tests/test_stages.py` case where Implement writes a valid report in a nested outbox path and assert it never reaches main."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
