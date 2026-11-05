# Review: snag

A base-red host check stays a failing report in checks.json, so a later Check retry tells the implementer to clear a pre-existing failure, which the ticket forbids.

## Findings

- [logic] chupa/stages.py:985 `check_hosts` appends each host report before base attribution and never changes it, so a base-red entry is written to `checks.json` as `verdict: "fail"` with its findings. `_prior_findings` returns every finding from a `fail` report when the prior terminal is a `gate_failed` Check, and `prior_attempts` presents those as "this attempt's to clear". So if a ticket fails Check on another gate while a host entry is red at base, the next Implement prompt lists the pre-existing host failure as work to fix. The ticket says red at base is charged to neither Check nor retry. Verification avoids this by marking `base_red` and excluding those results from its gate verdict. `test_base_red_entry_is_preexisting` pins the `fail` verdict and never exercises the retry path. (do instead: Keep the one report per run, but make a base-red entry's report carry no retry-visible failure: for example, replace it with a `pass` report with no findings once the base rerun is red, as Verification's `base_red` exclusion does. Update `test_base_red_entry_is_preexisting` to match, and assert that `_prior_findings` or `prior_attempts` omits the base-red finding after a Check that fails on another gate.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "7d3e0a2e5af71c4981eaa9d6082cbfd81aec6cae",
  "stem": "host-checks",
  "reviewed_sha": "7d3e0a2e5af71c4981eaa9d6082cbfd81aec6cae",
  "summary": "A base-red host check stays a failing report in checks.json, so a later Check retry tells the implementer to clear a pre-existing failure, which the ticket forbids.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/stages.py",
      "line": 985,
      "message": "`check_hosts` appends each host report before base attribution and never changes it, so a base-red entry is written to `checks.json` as `verdict: \"fail\"` with its findings. `_prior_findings` returns every finding from a `fail` report when the prior terminal is a `gate_failed` Check, and `prior_attempts` presents those as \"this attempt's to clear\". So if a ticket fails Check on another gate while a host entry is red at base, the next Implement prompt lists the pre-existing host failure as work to fix. The ticket says red at base is charged to neither Check nor retry. Verification avoids this by marking `base_red` and excluding those results from its gate verdict. `test_base_red_entry_is_preexisting` pins the `fail` verdict and never exercises the retry path.",
      "paved_road": "Keep the one report per run, but make a base-red entry's report carry no retry-visible failure: for example, replace it with a `pass` report with no findings once the base rerun is red, as Verification's `base_red` exclusion does. Update `test_base_red_entry_is_preexisting` to match, and assert that `_prior_findings` or `prior_attempts` omits the base-red finding after a Check that fails on another gate.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
