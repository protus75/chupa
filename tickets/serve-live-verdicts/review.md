# Review: snag

The keyed reject path is now tested and the live keep/reject/refusal flows look correct, but the diff adds an unrequested compatibility shim for the old confirm effect key and leaves runner.confirm_draft as a second, now-dead copy of the draft-promotion rules.

## Findings

- [scope] chupa/control.py:257 settle_admissions adds a backward-compatibility branch the ticket does not ask for. It looks up a completed effect under the legacy key `ticket-plane/<stem>/confirmed/<request_id>` and re-journals `draft_confirmed` from it. The ticket specifies a single key, `ticket-plane/<stem>/<verb>/<request_id>`, and the repo bans compat shims and parallel paths. If this branch is dropped, an old accepted confirm re-runs through the shared verdict function and either applies or completes with that function's refusal. That outcome is already covered. (do instead: Delete the `old_key`/`old` lookup and its `draft_confirmed` re-append. Every accepted null-hold_id request then runs only through `Effects(...).run(apply, key=f"ticket-plane/{stem}/{verb}/{request_id}")`.)
- [acceptance] chupa/runner.py:472 Scope-in requires one lock-free function holding every keep, kill and draft-promotion rule, so that there is one implementation of the verdict rules. After this diff, `runner.confirm_draft`, a separate draft-promotion implementation with its own stamp/commit/`draft_confirmed` logic, still exists. Its only live caller was serve's settle_admissions path, which this diff removed. `runner.committed_draft` likewise has no remaining caller. That leaves a second, unused copy of the draft-promotion rules alongside `verdict_locked`. (do instead: Remove `runner.confirm_draft` and `runner.committed_draft` from chupa/runner.py. `MergeQueue.confirm_draft` in chupa/mergequeue.py is now unreferenced and outside the fence, so file it in the Suggestion Box for removal instead of editing it here.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f346bfc92197bdd7ecac72a9af839ef17a58f720",
  "stem": "serve-live-verdicts",
  "reviewed_sha": "f346bfc92197bdd7ecac72a9af839ef17a58f720",
  "summary": "The keyed reject path is now tested and the live keep/reject/refusal flows look correct, but the diff adds an unrequested compatibility shim for the old confirm effect key and leaves runner.confirm_draft as a second, now-dead copy of the draft-promotion rules.",
  "findings": [
    {
      "code": "scope",
      "path": "chupa/control.py",
      "line": 257,
      "message": "settle_admissions adds a backward-compatibility branch the ticket does not ask for. It looks up a completed effect under the legacy key `ticket-plane/<stem>/confirmed/<request_id>` and re-journals `draft_confirmed` from it. The ticket specifies a single key, `ticket-plane/<stem>/<verb>/<request_id>`, and the repo bans compat shims and parallel paths. If this branch is dropped, an old accepted confirm re-runs through the shared verdict function and either applies or completes with that function's refusal. That outcome is already covered.",
      "paved_road": "Delete the `old_key`/`old` lookup and its `draft_confirmed` re-append. Every accepted null-hold_id request then runs only through `Effects(...).run(apply, key=f\"ticket-plane/{stem}/{verb}/{request_id}\")`.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "chupa/runner.py",
      "line": 472,
      "message": "Scope-in requires one lock-free function holding every keep, kill and draft-promotion rule, so that there is one implementation of the verdict rules. After this diff, `runner.confirm_draft`, a separate draft-promotion implementation with its own stamp/commit/`draft_confirmed` logic, still exists. Its only live caller was serve's settle_admissions path, which this diff removed. `runner.committed_draft` likewise has no remaining caller. That leaves a second, unused copy of the draft-promotion rules alongside `verdict_locked`.",
      "paved_road": "Remove `runner.confirm_draft` and `runner.committed_draft` from chupa/runner.py. `MergeQueue.confirm_draft` in chupa/mergequeue.py is now unreferenced and outside the fence, so file it in the Suggestion Box for removal instead of editing it here.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.3",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
