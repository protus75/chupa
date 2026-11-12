# Review: approve

`known` is now a required keyword-only parameter of `ControlInbox`, `control_inbox` and `PauseConsumer` with no default, and `build_control` passes it at construction; every caller in production code and the listed tests passes it, the new unit tests cover both constructors (omitting `known` raises `TypeError`, a supplied `known` reaches the inbox), the `build_control` stem rule is unchanged, and no doc states the old after-construction assignment.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "748178e8d0391a9364ac1e5003bc604d234d3034",
  "stem": "control-inbox-known-required",
  "reviewed_sha": "748178e8d0391a9364ac1e5003bc604d234d3034",
  "summary": "`known` is now a required keyword-only parameter of `ControlInbox`, `control_inbox` and `PauseConsumer` with no default, and `build_control` passes it at construction; every caller in production code and the listed tests passes it, the new unit tests cover both constructors (omitting `known` raises `TypeError`, a supplied `known` reaches the inbox), the `build_control` stem rule is unchanged, and no doc states the old after-construction assignment.",
  "findings": [],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
