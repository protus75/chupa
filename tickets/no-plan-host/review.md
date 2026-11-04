# Review: snag

The runtime plan reads are correctly routed through read_plan and tolerate an absent plan, but the carried reproducer breaks its specified protocol when an import fails, exiting 1 with empty stdout instead of printing the error result and exiting 2.

## Findings

- [acceptance] tests/regress_no_plan_host.py:14 The chupa and tests helper imports run at module level, outside main_result's try block. If any of them fails (for example a later rename of tests.test_drain.make_root or tests.test_cli.ENV, which this carried reproducer depends on), Python prints a traceback and exits 1 with nothing on stdout. The ticket requires `{"regression_result": "error"}` and exit 2 on any failure other than a FileNotFoundError naming CHUPA_PLAN.md. Exit 1 is also the code the ticket reserves for `defect`. (do instead: Move the chupa and tests imports into a function called inside main_result's try block (for example at the top of run() and no_plan()), so an import failure reaches `except Exception` and returns ("error", 2). Keep the sys.path insert at module level, and leave the JSON print as the only stdout output.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f7c128944bbdcd596db6705576e1ea4f42d0fdb8",
  "stem": "no-plan-host",
  "reviewed_sha": "f7c128944bbdcd596db6705576e1ea4f42d0fdb8",
  "summary": "The runtime plan reads are correctly routed through read_plan and tolerate an absent plan, but the carried reproducer breaks its specified protocol when an import fails, exiting 1 with empty stdout instead of printing the error result and exiting 2.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/regress_no_plan_host.py",
      "line": 14,
      "message": "The chupa and tests helper imports run at module level, outside main_result's try block. If any of them fails (for example a later rename of tests.test_drain.make_root or tests.test_cli.ENV, which this carried reproducer depends on), Python prints a traceback and exits 1 with nothing on stdout. The ticket requires `{\"regression_result\": \"error\"}` and exit 2 on any failure other than a FileNotFoundError naming CHUPA_PLAN.md. Exit 1 is also the code the ticket reserves for `defect`.",
      "paved_road": "Move the chupa and tests imports into a function called inside main_result's try block (for example at the top of run() and no_plan()), so an import failure reaches `except Exception` and returns (\"error\", 2). Keep the sys.path insert at module level, and leave the JSON print as the only stdout output.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.1",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
