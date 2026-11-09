---
id: tombstone-box-000248-d528f35a
kind: tombstone
link: declined-box-000128-16b156ae
reopen_after_days: 90
---
This note asks for a test that runs a ticket ending `already_satisfied` through `drive` and checks both the journaled terminal body and the exit code, once section 18 settles that exit code. Registry record 000128 already decided the same request.

This repeats declined-box-000128-16b156ae: the same missing test of `already_satisfied` through `drive` (journal body plus exit code), waiting on the same section 18 exit-code decision. The note gives no new evidence of incorrect runtime behavior. The merged `already-satisfied-settles` ticket has also since settled how this outcome is journaled.

- declined-box-000128-16b156ae covers the same missing `drive` test for `already_satisfied`, which waits on section 18's exit code
- declined-box-000123-687dd93a and tombstone-box-000246-7110b052 cover the exit-code question this test depends on
- Merged stem `already-satisfied-settles` settled the journal form of this outcome

Message: box-000248-d528f35a
