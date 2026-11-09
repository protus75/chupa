---
id: tombstone-box-000112-574f4aa7
kind: tombstone
link: host-checks
reopen_after_days: 90
---
A bootstrap note warned that host `review.mechanical` entries, including `trigger: always` hard checks, ran nowhere because no check runner existed, so a hard host check was skipped without notice. The merged `host-checks` ticket built that runner. Check now runs every triggered host entry, and merge re-runs the hard ones.

The fail-open gap the note describes is gone. `chupa/stages.py` `triggered_hosts` selects the configured `review.mechanical` entries, counting `trigger: always` as always triggered. `check_hosts` runs them during Check, and `chupa/merge.py:305` runs the hard entries again at the merge integration check. Registry record tombstone-box-000034 already credits `host-checks` with this runner, including its fail-closed handling of a crashed command.

- chupa/stages.py:970-975 triggered_hosts enumerates ctx.config.review.mechanical, matching trigger 'always' or a fence path and optionally only hard-severity entries
- chupa/stages.py:1138-1140 check_hosts runs every triggered host entry during Check
- chupa/merge.py:305 merge runs triggered_hosts(..., hard_only=True) on the integration candidate
- chupa/mergequeue.py:199-208 the merge queue reads review.mechanical for safety_checks
- host-checks is in the merged stems; registry tombstone-box-000034-bbf899f0 links the host check runner to host-checks

Message: box-000112-574f4aa7
