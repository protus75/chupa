# Review: snag

Stop is implemented correctly across control, drain (including the self-upgrade child), serve, the CLI and dev.py, but one docs statement about serve now describes the old behavior.

## Findings

- [acceptance] docs/how-chupa-works.md:- Section 2.1's verb table still says "| `serve` | yes | Runs the continuous daemon until `kill` or a signal (section 7.2). |". After this diff, serve also exits 0 when it accepts `stop` (serve.py run loop: `upgrade_stop = not self.control.projection.stop_requested; self.stop(); break`), so this row describes the old behavior. (do instead: Update the `serve` row in section 2.1 to say serve runs until `kill`, `stop`, or a signal. Optionally, add one sentence to section 7.2 saying an accepted `stop` waits for the same idle condition as the handoff and then exits without spawning.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "3faa54e361a52bc253b7c50393959814802c27ce",
  "stem": "stop-at-boundary",
  "reviewed_sha": "3faa54e361a52bc253b7c50393959814802c27ce",
  "summary": "Stop is implemented correctly across control, drain (including the self-upgrade child), serve, the CLI and dev.py, but one docs statement about serve now describes the old behavior.",
  "findings": [
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "Section 2.1's verb table still says \"| `serve` | yes | Runs the continuous daemon until `kill` or a signal (section 7.2). |\". After this diff, serve also exits 0 when it accepts `stop` (serve.py run loop: `upgrade_stop = not self.control.projection.stop_requested; self.stop(); break`), so this row describes the old behavior.",
      "paved_road": "Update the `serve` row in section 2.1 to say serve runs until `kill`, `stop`, or a signal. Optionally, add one sentence to section 7.2 saying an accepted `stop` waits for the same idle condition as the handoff and then exits without spawning.",
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
