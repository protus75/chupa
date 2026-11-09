---
id: tombstone-box-000199-f50854d0
kind: tombstone
link: tombstone-box-000013-7d15aaed
reopen_after_days: 90
---
A bootstrap note lists process-exec work still to build in `chupa/seams.py`: a synchronous `kill_group` with a spawn-time pgid hook, binding a run to its process group (`abort_current`, `chupa kill <run>`), and a `timeout=None` handoff mode with inherited stdio for self-upgrade. Registry record 000013 covers the same gap and found all of it built.

This message is a semantic duplicate of registry record tombstone-box-000013-7d15aaed. That record lists the same three pieces: synchronous kill_group with a spawn-time pgid hook, run-to-group binding (abort_current, chupa kill), and timeout=None with inherited stdio for the self-upgrade handoff. It records them as built by merged kill-executor-abort, and record 000067 points to that same record. The note reports no current harmful behavior.

- Registry tombstone-box-000013-7d15aaed lists the same kill_group/pgid hook, abort_current/chupa kill binding, and timeout=None inherited-stdio items and says they now exist.
- Registry tombstone-box-000067-e1460e52 also links to record 000013 and names merged kill-executor-abort, kill-cli-activation, and kill-signal-journal.
- Merged stems include kill-executor-abort, kill-cli-activation, kill-signal-journal, serve-self-upgrade, and drain-upgrade-own-source.

Message: box-000199-f50854d0
