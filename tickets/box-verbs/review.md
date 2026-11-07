# Review: snag

The verbs, status block, prompt kind, docs and tests meet the ticket, but the new top-level `except BoxError` in `main` catches every BoxError from every verb and gives the unknown-id advice for unrelated box failures.

## Findings

- [logic] chupa/__main__.py:469 `except BoxError` wraps the whole verb dispatch, so it catches every BoxError from any verb, not just unknown ids from triage, dismiss and prompt box. Every one of them now prints `-- name ids that chupa status lists` and exits 2. For example, a corrupt box file makes `chupa status`, `drain`, `run` or `serve` print `chupa status: invalid box file ... -- name ids that chupa status lists`. A RereportJournal conflict prints `conflicting reopen evidence; restore the journal-backed reopen signal -- name ids that chupa status lists`. Both point the operator at the wrong fix. (do instead: Give the unknown-id refusal only for unknown ids. One option: have `validate_ids` (and the box lookup in `ask.render`) catch the unknown-id BoxError and re-raise it as `runner.Refusal(f"unknown box id {id}", "name ids that chupa status lists")`. Then drop the blanket `except BoxError` from `main`, so other BoxErrors keep their old behavior.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f29ef5283f4a0dc428a645f3aa6b7d8c8e4deb34",
  "stem": "box-verbs",
  "reviewed_sha": "f29ef5283f4a0dc428a645f3aa6b7d8c8e4deb34",
  "summary": "The verbs, status block, prompt kind, docs and tests meet the ticket, but the new top-level `except BoxError` in `main` catches every BoxError from every verb and gives the unknown-id advice for unrelated box failures.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/__main__.py",
      "line": 469,
      "message": "`except BoxError` wraps the whole verb dispatch, so it catches every BoxError from any verb, not just unknown ids from triage, dismiss and prompt box. Every one of them now prints `-- name ids that chupa status lists` and exits 2. For example, a corrupt box file makes `chupa status`, `drain`, `run` or `serve` print `chupa status: invalid box file ... -- name ids that chupa status lists`. A RereportJournal conflict prints `conflicting reopen evidence; restore the journal-backed reopen signal -- name ids that chupa status lists`. Both point the operator at the wrong fix.",
      "paved_road": "Give the unknown-id refusal only for unknown ids. One option: have `validate_ids` (and the box lookup in `ask.render`) catch the unknown-id BoxError and re-raise it as `runner.Refusal(f\"unknown box id {id}\", \"name ids that chupa status lists\")`. Then drop the blanket `except BoxError` from `main`, so other BoxErrors keep their old behavior.",
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
