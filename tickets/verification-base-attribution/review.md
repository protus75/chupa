# Review: snag

The attribution logic and cleanup look correct, but the test_stages.py base-red test does not prove acceptance criterion 1: it uses the default one-command ticket instead of a ticket with two Verification commands, one base-red and one green.

## Findings

- [acceptance] tests/test_stages.py:380 Criterion 1 needs a ticket with TWO Verification commands, one red at both base and branch and one green, that passes Check. `test_base_red_verification_passes_check_files_a_report_and_cleans_worktree` runs the default fixture ticket, which has only `grep -q ok chupa/thing.py`. So it never shows that a green command beside a base-red one is unaffected, and it never shows that only the red command is marked `base_red` (it checks `verification[0]` only). (do instead: Give the test a two-command `## Verification` ticket, for example via the `TICKET.replace` pattern `_report_ticket` uses: one command red at both base and branch, and one always green (e.g. `test -f chupa/thing.py`). Assert Check is ok, `invoice.verification[0].base_red is True`, `invoice.verification[1].base_red is False` with rc 0, and exactly one `failure_report` with outcome `base_red` and origin STEM.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "4e6bfe6124652250d10fa209126ee419cee0f784",
  "stem": "verification-base-attribution",
  "reviewed_sha": "4e6bfe6124652250d10fa209126ee419cee0f784",
  "summary": "The attribution logic and cleanup look correct, but the test_stages.py base-red test does not prove acceptance criterion 1: it uses the default one-command ticket instead of a ticket with two Verification commands, one base-red and one green.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_stages.py",
      "line": 380,
      "message": "Criterion 1 needs a ticket with TWO Verification commands, one red at both base and branch and one green, that passes Check. `test_base_red_verification_passes_check_files_a_report_and_cleans_worktree` runs the default fixture ticket, which has only `grep -q ok chupa/thing.py`. So it never shows that a green command beside a base-red one is unaffected, and it never shows that only the red command is marked `base_red` (it checks `verification[0]` only).",
      "paved_road": "Give the test a two-command `## Verification` ticket, for example via the `TICKET.replace` pattern `_report_ticket` uses: one command red at both base and branch, and one always green (e.g. `test -f chupa/thing.py`). Assert Check is ok, `invoice.verification[0].base_red is True`, `invoice.verification[1].base_red is False` with rc 0, and exactly one `failure_report` with outcome `base_red` and origin STEM."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
