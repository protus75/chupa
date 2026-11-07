---
id: decision-box-000020-39c3bb06
kind: decision
link: box-000020-39c3bb06
reopen_after_days: 90
---
The engine lock in `chupa/lockfile.py` is an flock on a descriptor that is not passed on through exec. A child made by a plain `fork()`, for example a multiprocessing pool using the fork start method, still shares that descriptor's open file description, so the child would keep holding the lock after the parent releases it. The self-upgrade handoff goes through exec, not fork, so the note only asks to document the caveat if a fork-based consumer ever appears.

Nothing in the engine triggers this today. The note itself calls it latent, and the engine package never calls `os.fork`, imports `multiprocessing`, uses `ProcessPoolExecutor`, or sets a start method. Every child process is started through the process-exec seam, and the descriptor is marked not to pass through exec. Since no child keeps the lock, this is speculative hardening or a docstring note with no harmful runtime effect. The registry already holds three related lockfile decisions (000017, 000018, 000019), but this note covers a different case (sharing the lock through fork), so it is not a duplicate.

- Searching `chupa/` for `os.fork|multiprocessing|ProcessPoolExecutor|set_start_method` returns no matches.
- The message says the self-upgrade handoff uses the process-exec seam, which execs and so drops the non-inheritable lock descriptor.
- Related lockfile decisions decision-box-000017-e78ba696, decision-box-000018-8a8d965d and decision-box-000019-cecc4542 deal with seam use, the inheritance test, and inode replacement, not with sharing the lock through fork.

Message: box-000020-39c3bb06
