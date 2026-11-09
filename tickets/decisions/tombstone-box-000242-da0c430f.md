---
id: tombstone-box-000242-da0c430f
kind: tombstone
link: host-checks
reopen_after_days: 30
---
A bootstrap note said host `review.mechanical` entries, including `trigger: always` hard checks, were never run by Check or merge because no check runner existed, so a hard host check was skipped without notice. It asked for the section 7 check-runner contract, or a config refusal until one existed. The merged `host-checks` ticket built that runner.

This message makes the same report as registry record tombstone-box-000112-574f4aa7, which linked it to the merged ticket `host-checks`. That ticket built the host check runner. Check now runs every triggered host entry, merge re-runs the hard ones, and a crashed, timed-out or missing host command fails closed as a finding. The gap is gone.

- Merged stems include `host-checks`.
- Registry tombstone-box-000112-574f4aa7: host `review.mechanical` hard checks ran nowhere; `host-checks` built the runner; Check runs triggered host entries and merge re-runs the hard ones.
- Registry tombstone-box-000034-bbf899f0: the `host-checks` runner turns a crashed, timed-out or missing-executable host command into a failing finding with a paved road.

Message: box-000242-da0c430f
