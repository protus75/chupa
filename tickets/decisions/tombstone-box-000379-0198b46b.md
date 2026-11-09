---
id: tombstone-box-000379-0198b46b
kind: tombstone
link: implement-spec-run-coverage-gate
reopen_after_days: 30
---
The note says a ticket's Verification runs `./dev.py test`, which does not apply the unit covgate per-file floors in test-gate.toml. So an implementer first sees a coverage-floor miss at Check (seen on check-test-timing, 2026-11-08).

This duplicates the open ticket implement-spec-run-coverage-gate. That ticket requires Implement to run each hard coverage gate the host's Check configures once after its last edit, so a floor miss is found before Check. Registry record tombstone-box-000373-3c722d34 already tombstoned the same report, with the same check-test-timing evidence, against that ticket.

- Open ticket implement-spec-run-coverage-gate: Task step 3 makes Implement run the hard coverage gates (`review.mechanical` entries with a `coverage` report) once after its last edit when the diff touches a measured file.
- Registry tombstone-box-000373-3c722d34 has the same summary (Verification runs `./dev.py test`, which skips the unit covgate floors; seen on check-test-timing 2026-11-08) and links to implement-spec-run-coverage-gate.

Message: box-000379-0198b46b
