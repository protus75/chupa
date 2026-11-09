---
id: declined-box-000192-09173d9a
kind: declined
link: box-000192-09173d9a
reopen_after_days: 60
---
The suggestion is that the Verification base-attribution rerun stop treating a base command that times out or cannot run (rc=None) as `base_red`. The worry is that a hang the branch introduces could be excused when the same command is also slow on main.

The code does what the note describes. In `gather_evidence` (`chupa/stages.py:884-890`), a base rerun that times out sets rc=None, the `rc != 0` check passes, and the command is marked `base_red`. But this follows the existing rule: rc=None fails closed like a non-zero exit (`CommandResult` comment at line 690). A command that cannot finish within the stuck budget on the merge base really is red on main. The engine also files a `failure_report` with outcome `base_red` telling the operator to fix main, so the excuse is never silent. The message cites no incident in which a branch-introduced hang merged because of this path. It is a speculative hardening proposal, not a demonstrated harmful gap. The open ticket `base-red-subject-exists-at-base` deals with a separate, demonstrated false-excuse path: subjects that are absent at the base.

- chupa/stages.py:884-890: on base rerun timeout, rc=None and `if rc != 0` marks results[n-1] base_red=True
- chupa/stages.py:690: CommandResult documents rc=None as failing closed like a nonzero exit
- chupa/stages.py:891-896: every base_red attribution enqueues a deduplicated failure_report telling the operator to fix main
- chupa/stages.py:1223: VerificationGate skips only results with base_red set
- The message is a bootstrap-ingest review suggestion with no stage, outcome, or run showing a hang that was excused and merged

Message: box-000192-09173d9a
