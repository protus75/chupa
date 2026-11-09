# Review: snag

The implementation mostly matches the ticket, but no test refuses an otherwise-valid schema-1 document, evaluate picks its value by the check name instead of using the coverage it is given, and section 12 of how-chupa-works.md still says schemas 1 and 2 are accepted.

## Findings

- [acceptance] tests/integration/test_testreport.py:74 Acceptance 1 requires a test proving a schema-1 document raises ResultsInvalid. Every schema-1 case in test_invalid_results is also invalid for another reason: an `error` outcome, a blank node ID, an extra key, or a list for `tests`. Under the old reader, which accepted schema 1, each of these was still refused. So the suite passes even if schema 1 were still accepted. (do instead: Add a schema-1 case to the refused parametrize list that is otherwise valid, such as {"schema_version": 1, "tests": {"test_a": "passed"}}.)
- [acceptance] tests/unit/test_testreport_reader.py:8 The ticket says a schema-1 document joins the refused cases here. The only schema-1 cases in test_invalid_results also fail the old reader for other reasons: they have a `seconds` key, a list for `tests`, a blank node ID, or an `error` outcome. Accepting a valid schema-1 document would therefore go undetected. (do instead: Add {"schema_version": 1, "tests": {"test_a": "passed"}} to the refused cases.)
- [logic] chupa/covgate.py:123 check() chooses its value with `repository if name == "repository" else percent(paths)`, so it decides by the check name and ignores the paths it was given. A gate package key `repository`, or a file at the repository root named `repository`, gets the repository-wide percent instead of its own, so evaluate's results change. evaluate also re-implements the covered/total formula in a local percent() instead of using what percentages returns. That is a second copy of the formula that can drift. (do instead: Pass the repository value into the repository check explicitly. For example, pass the value instead of paths, or use percentages()' per-file map for file checks and compute only package aggregates locally. Never branch on the check name.)
- [acceptance] docs/how-chupa-works.md:- The section 12 `chupa.testreport` bullet still says "The results reader accepts schemas 1 and 2; schema 2 also contains a matching `seconds` map of finite nonnegative floats." The reader now refuses schema 1. (do instead: Change the sentence to say the reader accepts only schema 2 and refuses schema 1.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "8c62e23faa5e9e76e92529521d57b61c5e37db9d",
  "stem": "check-test-timing",
  "reviewed_sha": "8c62e23faa5e9e76e92529521d57b61c5e37db9d",
  "summary": "The implementation mostly matches the ticket, but no test refuses an otherwise-valid schema-1 document, evaluate picks its value by the check name instead of using the coverage it is given, and section 12 of how-chupa-works.md still says schemas 1 and 2 are accepted.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/integration/test_testreport.py",
      "line": 74,
      "message": "Acceptance 1 requires a test proving a schema-1 document raises ResultsInvalid. Every schema-1 case in test_invalid_results is also invalid for another reason: an `error` outcome, a blank node ID, an extra key, or a list for `tests`. Under the old reader, which accepted schema 1, each of these was still refused. So the suite passes even if schema 1 were still accepted.",
      "paved_road": "Add a schema-1 case to the refused parametrize list that is otherwise valid, such as {\"schema_version\": 1, \"tests\": {\"test_a\": \"passed\"}}.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/unit/test_testreport_reader.py",
      "line": 8,
      "message": "The ticket says a schema-1 document joins the refused cases here. The only schema-1 cases in test_invalid_results also fail the old reader for other reasons: they have a `seconds` key, a list for `tests`, a blank node ID, or an `error` outcome. Accepting a valid schema-1 document would therefore go undetected.",
      "paved_road": "Add {\"schema_version\": 1, \"tests\": {\"test_a\": \"passed\"}} to the refused cases.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/covgate.py",
      "line": 123,
      "message": "check() chooses its value with `repository if name == \"repository\" else percent(paths)`, so it decides by the check name and ignores the paths it was given. A gate package key `repository`, or a file at the repository root named `repository`, gets the repository-wide percent instead of its own, so evaluate's results change. evaluate also re-implements the covered/total formula in a local percent() instead of using what percentages returns. That is a second copy of the formula that can drift.",
      "paved_road": "Pass the repository value into the repository check explicitly. For example, pass the value instead of paths, or use percentages()' per-file map for file checks and compute only package aggregates locally. Never branch on the check name.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "The section 12 `chupa.testreport` bullet still says \"The results reader accepts schemas 1 and 2; schema 2 also contains a matching `seconds` map of finite nonnegative floats.\" The reader now refuses schema 1.",
      "paved_road": "Change the sentence to say the reader accepts only schema 2 and refuses schema 1.",
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
