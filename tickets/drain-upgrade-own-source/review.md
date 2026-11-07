# Review: approve

The diff limits drain self-upgrade to merges in the engine's own resolved source tree, makes reexec_argv read ENGINE at call time, patches ENGINE in every test that expects a handoff, adds the host-repo test that expects no re-exec, and updates the docs section 7.1 statement.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "d96bd79f4ed7551ff9e43b626a77a49bd71a5bfd",
  "stem": "drain-upgrade-own-source",
  "reviewed_sha": "d96bd79f4ed7551ff9e43b626a77a49bd71a5bfd",
  "summary": "The diff limits drain self-upgrade to merges in the engine's own resolved source tree, makes reexec_argv read ENGINE at call time, patches ENGINE in every test that expects a handoff, adds the host-repo test that expects no re-exec, and updates the docs section 7.1 statement.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
