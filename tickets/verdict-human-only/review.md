# Review: snag

The gating, typed-stem prompt, `dev.py` and docs meet the ticket, but the new state preview crashes on a malformed ticket file before intake can issue its paved-road refusal.

## Findings

- [logic] chupa/__main__.py:458 `_verdict` now calls `runner._ticket_state(path)` before `runner.verdict` runs intake. `_ticket_state` does an unguarded `yaml.safe_load(split[0]).get("state")`. If `tickets/<stem>/ticket.md` has invalid YAML frontmatter and the stem is neither held nor queued, `yaml.YAMLError` escapes. Non-mapping frontmatter raises `AttributeError` instead. `main`'s except list catches neither, so a person at a terminal gets a raw traceback. Before this diff, the same input reached intake and produced a refusal with exit 2 and the paved road "fix the ticket and retry the verdict". (do instead: Make the preview tolerate unparseable frontmatter, for example by using `_load_frontmatter` or `validate_ticket` semantics and showing an 'invalid ticket' state or raising `runner.Refusal` with the fix-the-ticket road. Add a test that runs a verdict on a stem with malformed frontmatter and asserts exit 2 with the paved road and no state change.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "ae396c081abc493c345f797be9108c2b1fcc3c77",
  "stem": "verdict-human-only",
  "reviewed_sha": "ae396c081abc493c345f797be9108c2b1fcc3c77",
  "summary": "The gating, typed-stem prompt, `dev.py` and docs meet the ticket, but the new state preview crashes on a malformed ticket file before intake can issue its paved-road refusal.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/__main__.py",
      "line": 458,
      "message": "`_verdict` now calls `runner._ticket_state(path)` before `runner.verdict` runs intake. `_ticket_state` does an unguarded `yaml.safe_load(split[0]).get(\"state\")`. If `tickets/<stem>/ticket.md` has invalid YAML frontmatter and the stem is neither held nor queued, `yaml.YAMLError` escapes. Non-mapping frontmatter raises `AttributeError` instead. `main`'s except list catches neither, so a person at a terminal gets a raw traceback. Before this diff, the same input reached intake and produced a refusal with exit 2 and the paved road \"fix the ticket and retry the verdict\".",
      "paved_road": "Make the preview tolerate unparseable frontmatter, for example by using `_load_frontmatter` or `validate_ticket` semantics and showing an 'invalid ticket' state or raising `runner.Refusal` with the fix-the-ticket road. Add a test that runs a verdict on a stem with malformed frontmatter and asserts exit 2 with the paved road and no state change.",
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
