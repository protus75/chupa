# Review: snag

Review of the code is finished and the verdict is snag: `chupa lint` disagrees with intake on new-ticket frontmatter claims, and it exits 1 instead of 2 for a named stem with no ticket file when the stem name is invalid or reserved.

## Findings

- [acceptance] chupa/__main__.py:322 Lint validates the raw file, but intake first applies `_intake_claims` to a new stem, so the two apply different rules, which the ticket's Definition of rejected forbids. A new ticket that omits `source:` or `state:` is admitted by intake, which stamps them (its own refusal road says to drop the `source:` line), yet lint exits 1 with `frontmatter source: Field required`. A new stem with `source: seed` or `state: merged` passes lint, yet intake refuses it. `tests/test_lint_verb.py` `valid_ticket()` has to add both keys to the shared `tests/test_cli.py` ticket fixture to get a pass. (do instead: Before `validate_ticket`, apply the same claims step intake uses for a stem with no committed predecessor, determining newness with a read-only git query, and validate the stamped text without writing it. Add tests for an omitted `source`/`state` (valid) and a new `source: seed` (finding).)
- [logic] chupa/__main__.py:319 The ticket requires exit 2 for a named stem with no ticket file, but `stem_findings` runs first and skips the file read. `chupa lint ../escape`, `chupa lint Bad_Stem`, or `chupa lint retro` therefore exits 1 with a rename or reserved-stem finding, even though no ticket file exists. `test_lint_named_stems_and_missing_stem` pins this with `lint(root, "../escape") == 1`. (do instead: For a named stem, report a missing ticket file with exit 2 before judging the stem name, and keep exit 1 for an invalid stem whose ticket file exists. Change the test to assert exit 2 for the missing-file case.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "4270c76643cdd88021ae1587734b188dbc640547",
  "stem": "lint-verb",
  "reviewed_sha": "4270c76643cdd88021ae1587734b188dbc640547",
  "summary": "Review of the code is finished and the verdict is snag: `chupa lint` disagrees with intake on new-ticket frontmatter claims, and it exits 1 instead of 2 for a named stem with no ticket file when the stem name is invalid or reserved.",
  "findings": [
    {
      "code": "acceptance",
      "path": "chupa/__main__.py",
      "line": 322,
      "message": "Lint validates the raw file, but intake first applies `_intake_claims` to a new stem, so the two apply different rules, which the ticket's Definition of rejected forbids. A new ticket that omits `source:` or `state:` is admitted by intake, which stamps them (its own refusal road says to drop the `source:` line), yet lint exits 1 with `frontmatter source: Field required`. A new stem with `source: seed` or `state: merged` passes lint, yet intake refuses it. `tests/test_lint_verb.py` `valid_ticket()` has to add both keys to the shared `tests/test_cli.py` ticket fixture to get a pass.",
      "paved_road": "Before `validate_ticket`, apply the same claims step intake uses for a stem with no committed predecessor, determining newness with a read-only git query, and validate the stamped text without writing it. Add tests for an omitted `source`/`state` (valid) and a new `source: seed` (finding).",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/__main__.py",
      "line": 319,
      "message": "The ticket requires exit 2 for a named stem with no ticket file, but `stem_findings` runs first and skips the file read. `chupa lint ../escape`, `chupa lint Bad_Stem`, or `chupa lint retro` therefore exits 1 with a rename or reserved-stem finding, even though no ticket file exists. `test_lint_named_stems_and_missing_stem` pins this with `lint(root, \"../escape\") == 1`.",
      "paved_road": "For a named stem, report a missing ticket file with exit 2 before judging the stem name, and keep exit 1 for an invalid stem whose ticket file exists. Change the test to assert exit 2 for the missing-file case.",
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
