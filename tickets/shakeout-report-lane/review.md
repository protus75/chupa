# Review: snag

lift_outbox validates every registered outbox file on every lift kind and ignores the `only` filter. As a result, an invalid report, whether left behind by a failed Check or written by the Implement agent, raises an unhandled ArtifactInvalid out of the run-record, harvest and diagnosis lifts.

## Findings

- [logic] chupa/stages.py:302 The validation loop runs over all outbox candidates for every lift kind and ignores `only`. When a Check fails on a schema-invalid shakeout-report.json, the invalid file stays in the outbox. The runner's next lift then raises ArtifactInvalid again: harvest (`only=attempts/N/harvest.json`) is swallowed as harvest_failed, and write_diagnosis (`only=diagnosis.json`) is uncaught and crashes drive. Likewise, an Implement agent that writes an invalid shakeout-report.json makes the run-record lift in `implement` raise uncaught, crashing the stage instead of producing a terminal outcome. Non-checks lifts never carry the registered artifact, so validating it there only adds crash paths. (do instead: Validate only the registered files that this lift will actually carry, i.e. when kind == "checks" and the file passes `written`/`only`. Also remove the invalid registered artifact from the outbox when `check` returns gate_failed on ArtifactInvalid, so later harvest and diagnosis lifts proceed. Add a test that drives the invalid-report path through harvest and diagnosis.)
- [acceptance] tests/test_stages.py:393 AC1 requires the schema-invalid Check to commit neither file. The test only asserts that the report is absent from the repo. It never checks that checks.json was not committed or that no `chupa(<stem>): checks` commit exists. (do instead: Also assert that `tickets/<stem>/checks.json` is absent from the repo and that `chupa(<stem>): checks` is not in subjects(repo).)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "d351fa2e93d5d41e6099f601d781102f038aca82",
  "stem": "shakeout-report-lane",
  "reviewed_sha": "d351fa2e93d5d41e6099f601d781102f038aca82",
  "summary": "lift_outbox validates every registered outbox file on every lift kind and ignores the `only` filter. As a result, an invalid report, whether left behind by a failed Check or written by the Implement agent, raises an unhandled ArtifactInvalid out of the run-record, harvest and diagnosis lifts.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/stages.py",
      "line": 302,
      "message": "The validation loop runs over all outbox candidates for every lift kind and ignores `only`. When a Check fails on a schema-invalid shakeout-report.json, the invalid file stays in the outbox. The runner's next lift then raises ArtifactInvalid again: harvest (`only=attempts/N/harvest.json`) is swallowed as harvest_failed, and write_diagnosis (`only=diagnosis.json`) is uncaught and crashes drive. Likewise, an Implement agent that writes an invalid shakeout-report.json makes the run-record lift in `implement` raise uncaught, crashing the stage instead of producing a terminal outcome. Non-checks lifts never carry the registered artifact, so validating it there only adds crash paths.",
      "paved_road": "Validate only the registered files that this lift will actually carry, i.e. when kind == \"checks\" and the file passes `written`/`only`. Also remove the invalid registered artifact from the outbox when `check` returns gate_failed on ArtifactInvalid, so later harvest and diagnosis lifts proceed. Add a test that drives the invalid-report path through harvest and diagnosis."
    },
    {
      "code": "acceptance",
      "path": "tests/test_stages.py",
      "line": 393,
      "message": "AC1 requires the schema-invalid Check to commit neither file. The test only asserts that the report is absent from the repo. It never checks that checks.json was not committed or that no `chupa(<stem>): checks` commit exists.",
      "paved_road": "Also assert that `tickets/<stem>/checks.json` is absent from the repo and that `chupa(<stem>): checks` is not in subjects(repo)."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
