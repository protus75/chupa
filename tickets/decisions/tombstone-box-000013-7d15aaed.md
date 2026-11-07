---
id: tombstone-box-000013-7d15aaed
kind: tombstone
link: kill-executor-abort
reopen_after_days: 90
---
A bootstrap note listed process-exec pieces still to build: a synchronous `kill_group` with a spawn-time pgid hook, binding a run to its process group (`abort_current`, `chupa kill <run>`), and an unbounded `timeout=None` mode with inherited stdio for the self-upgrade handoff. All of them now exist.

Merged tickets built everything the note deferred. kill-executor-abort, kill-cli-activation and kill-worker-stop added the group kill and the run-to-group binding. serve-self-upgrade and drain-upgrade-own-source added the inherited-stdio handoff. No behavior gap is left. kill-executor-abort is the main match because it delivers the run abort path the note centres on.

- chupa/seams.py:53 adds `kill_group(pgid)` to the ProcessExec protocol, and chupa/seams.py:167 implements it with `os.killpg(pgid, SIGKILL)`.
- chupa/seams.py:49 and :136 add an `on_spawn` hook that gets the child pid, which is also its pgid because of start_new_session.
- chupa/seams.py:109-111: `timeout=None` gives the child inherited stdio (stream=None) for the self-upgrade handoff child.
- chupa/providers.py:421 calls `self._exec.kill_group(self._pgid)`, and providers.py:627, driver.py:425, stages.py:273 and daemon.py:467 bind runs to `abort_current`.
- chupa/drain.py:263 and :511 send kill through `dispatch.abort_current`, and chupa/serve.py:629 and drain.py:294 use `timeout=None` for the reexec handoff.
- Merged stems: kill-executor-abort, kill-cli-activation, kill-worker-stop, serve-self-upgrade, drain-upgrade-own-source.

Message: box-000013-7d15aaed
