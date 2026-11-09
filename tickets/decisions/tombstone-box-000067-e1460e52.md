---
id: tombstone-box-000067-e1460e52
kind: tombstone
link: tombstone-box-000013-7d15aaed
reopen_after_days: 90
---
This bootstrap note says the process-exec seam gained a spawn-time pgid hook and a synchronous `kill_group` for `abort_current`, and that `chupa kill <run>` still could not find a run's process group. Registry record 000013 already covers the same gap and found the binding built. The merged tickets kill-executor-abort, kill-cli-activation and kill-signal-journal delivered it.

This is the same request as tombstone-box-000013-7d15aaed, which listed the `kill_group`/pgid hook and the run-to-group binding (`abort_current`, `chupa kill <run>`) as outstanding and was closed because all of them exist. The current code still matches that closure: the daemon handles an accepted `kill` control verb by calling `abort_current` down the provider chain, and that call reaches `kill_group` on the recorded pgid.

- chupa/seams.py:53 and :167 define `kill_group(pgid)` on the exec protocol and on SubprocessExec
- chupa/providers.py:421 calls `self._exec.kill_group(self._pgid)`; providers.py:627 `abort_current`
- chupa/daemon.py:273 handles an accepted `kill` control verb bound to the lifecycle_id; daemon.py:78 `executor_abort` and :467 `abort_current`
- chupa/driver.py:425 and stages.py:273 pass `abort_current` down to the LLM
- Merged stems: kill-executor-abort, kill-cli-activation, kill-signal-journal, kill-worker-stop, kill-failure-suppression
- Registry tombstone-box-000013-7d15aaed (link kill-executor-abort) records the same pieces as built

Message: box-000067-e1460e52
