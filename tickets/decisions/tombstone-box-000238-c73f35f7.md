---
id: tombstone-box-000238-c73f35f7
kind: tombstone
link: declined-box-000097-cd50f4c0
reopen_after_days: 30
---
When `run` or `main` hits an engine exception that is not one of the named refusals (for example a GitError from intake or describe, an OSError, or a ValueError from the stage seam), the CLI exits 1 with a traceback. Under the section 18 exit contract, exit 1 means a ticket ended in a non-ok terminal state, so a crash and a failed ticket look the same to a wrapper. The proposal is to map unexpected engine exceptions to exit 2 or to a separate crash exit path.

Registry record declined-box-000097-cd50f4c0 already decided this request: exceptions outside the named refusal list exit 1 with a traceback and collide with section 18's meaning of exit 1, and the proposed fix was exit 2 or a crash path. Record tombstone-box-000124-5512b514 already points to it for the same gap. This message adds no new evidence and no reported incident.

- declined-box-000097-cd50f4c0 describes the same problem: only the fixed refusal list maps to exit 2, while GitError, OSError and ValueError escape with exit 1, which collides with section 18.
- tombstone-box-000124-5512b514 already links this same gap to declined-box-000097-cd50f4c0.
- The message cites no new crash that a wrapper misread as a ticket outcome.

Message: box-000238-c73f35f7
