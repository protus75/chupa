# Review: snag

The skip logic, the shared decision function, the queue tiering and the tests match the ticket, but section 5.4 of docs/how-chupa-works.md still describes the old unconditional merge-time host-check reruns.

## Findings

- [acceptance] docs/how-chupa-works.md:- Section 5.4 (Host checks) still says without qualification: "Inline merge reruns triggered hard entries on the rebased candidate. The `serve` merge queue (section 7.2) runs the hard entries named in `merge.safety_checks` at safety and every always/hard entry at integration." After this diff, both reruns are skipped for a nonempty branch when main changed only `tickets/` paths since the reviewed merge base. The doc therefore states the old behavior. (do instead: Qualify the section 5.4 sentences: inline merge and the serve queue's safety host checks and integration tier rerun only when main changed a path outside `tickets/` since the reviewed merge base, or when the branch diff is empty. Otherwise only the Merge gates run (see sections 4.5 and 7.2.1).)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "2530be735a8b46e8952e82863b3233ce95f27167",
  "stem": "merge-skip-unchanged",
  "reviewed_sha": "2530be735a8b46e8952e82863b3233ce95f27167",
  "summary": "The skip logic, the shared decision function, the queue tiering and the tests match the ticket, but section 5.4 of docs/how-chupa-works.md still describes the old unconditional merge-time host-check reruns.",
  "findings": [
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "Section 5.4 (Host checks) still says without qualification: \"Inline merge reruns triggered hard entries on the rebased candidate. The `serve` merge queue (section 7.2) runs the hard entries named in `merge.safety_checks` at safety and every always/hard entry at integration.\" After this diff, both reruns are skipped for a nonempty branch when main changed only `tickets/` paths since the reviewed merge base. The doc therefore states the old behavior.",
      "paved_road": "Qualify the section 5.4 sentences: inline merge and the serve queue's safety host checks and integration tier rerun only when main changed a path outside `tickets/` since the reviewed merge base, or when the branch diff is empty. Otherwise only the Merge gates run (see sections 4.5 and 7.2.1).",
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
