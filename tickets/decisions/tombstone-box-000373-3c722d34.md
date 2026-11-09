---
id: tombstone-box-000373-3c722d34
kind: tombstone
link: implement-spec-run-coverage-gate
reopen_after_days: 30
---
A ticket's Verification runs `./dev.py test`, which does not apply the unit covgate per-file coverage floors. Implement therefore first sees a coverage-floor miss when Check runs. This was observed on check-test-timing on 2026-11-08.

Open ticket implement-spec-run-coverage-gate already covers this gap. Implement replies `ok` after running only the `## Verification` commands, and the hard `unit` coverage gate then fails at Check. That ticket adds a Task step requiring Implement to run each hard coverage gate the host's Check configures once after its last edit. This message reports the same behavior on a different ticket and does not show a separate cause.

- Open ticket implement-spec-run-coverage-gate: Implement replied ok after running only Verification commands and the hard coverage gate (`unit`) then failed at Check (results-schema-2-reader, review-lock-only-for-intake, core-drift-preflight).
- That ticket's fix requires Implement to run each hard coverage gate (the `review.mechanical` entries with a `coverage` report) once after its last edit, whenever the diff touches a measured file.
- The message reports the same symptom: coverage-floor misses found only at Check because Verification uses `./dev.py test` without covgate floors.

Message: box-000373-3c722d34
