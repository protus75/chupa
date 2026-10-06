# Review: snag

The attribution logic and tests match the ticket, but the diff adds a required `verification` field to the persisted `Invoice` schema, so every checks.json written before this change no longer validates.

## Findings

- [logic] chupa/stages.py:117 `Invoice` is strict with extra=forbid. This diff adds `verification: list["CommandResult"]` as a required field with no default. Twenty checks.json files already on main lack the field (for example tickets/box-triage/checks.json). They are still read through `Invoice.model_validate_json`: `_prior_seed_reviews` reads `main:tickets/<stem>/checks.json` and does not catch ValidationError, `_prior_findings` reads the canonical-dir checks.json when a gate_failed ticket re-enters, and merge's seed gate reads `seed_checks_text`. Re-running any of those stems after this change raises a ValidationError or, in the seed gate, refuses with 'does not parse', even though the ticket did nothing wrong. (do instead: Give the field a default like the neighbouring `seeds` field (`verification: list["CommandResult"] = []`), so older checks.json files still validate while new ones record `base_red`. Add a test that a checks.json without `verification` still parses through `_prior_findings`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f4f78e2a99871b8e715fd36ac2a51aa0b30a07c1",
  "stem": "verification-base-attribution",
  "reviewed_sha": "f4f78e2a99871b8e715fd36ac2a51aa0b30a07c1",
  "summary": "The attribution logic and tests match the ticket, but the diff adds a required `verification` field to the persisted `Invoice` schema, so every checks.json written before this change no longer validates.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/stages.py",
      "line": 117,
      "message": "`Invoice` is strict with extra=forbid. This diff adds `verification: list[\"CommandResult\"]` as a required field with no default. Twenty checks.json files already on main lack the field (for example tickets/box-triage/checks.json). They are still read through `Invoice.model_validate_json`: `_prior_seed_reviews` reads `main:tickets/<stem>/checks.json` and does not catch ValidationError, `_prior_findings` reads the canonical-dir checks.json when a gate_failed ticket re-enters, and merge's seed gate reads `seed_checks_text`. Re-running any of those stems after this change raises a ValidationError or, in the seed gate, refuses with 'does not parse', even though the ticket did nothing wrong.",
      "paved_road": "Give the field a default like the neighbouring `seeds` field (`verification: list[\"CommandResult\"] = []`), so older checks.json files still validate while new ones record `base_red`. Add a test that a checks.json without `verification` still parses through `_prior_findings`."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
