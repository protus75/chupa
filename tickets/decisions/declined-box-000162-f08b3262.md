---
id: declined-box-000162-f08b3262
kind: declined
link: box-000162-f08b3262
reopen_after_days: 90
---
A review note from the spine-harvest batch said `drive`'s docstring still claimed a non-ok run leaves its ticket, branch and worktree in place, even though harvest now wipes the worktree at every non-ok terminal. It asked the ticket to update that docstring and to test that a re-offer recreates the worktree on the kept branch. The docstring has since been updated.

Nothing wrong happens at runtime. The docstring at `chupa/runner.py:148` now reads "Implement -> Check -> Review -> Merge; harvest, dispatch, journal, then wipe a non-ok run." That matches the wipe behavior, and the old phrase no longer appears anywhere in `chupa/`. The other half of the request asks for one more test of re-offer worktree recreation. No failure is reported, so that is a test-only improvement and does not meet the admission bar.

- chupa/runner.py:147-148 `drive` docstring: "harvest, dispatch, journal, then wipe a non-ok run."
- grep for "in place for the operator" / "leaves the ticket" in chupa/ returns no matches
- spine-harvest is merged
- related prior decision declined-box-000122-6f939062 about non-ok terminal worktree wipe

Message: box-000162-f08b3262
