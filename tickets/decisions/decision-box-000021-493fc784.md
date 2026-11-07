---
id: decision-box-000021-493fc784
kind: decision
link: box-000021-493fc784
reopen_after_days: 180
---
When `chupa/lockfile.py` takes the lock, it empties the lock file (`os.ftruncate(fd, 0)`) and then writes the holder identity (`os.pwrite`). A process that fails to get the lock and reads the file between those two calls gets no holder, so `LockHeld` reports an unknown holder. The suggestion is to write the identity first and then truncate the file to that length, which makes the empty-file window shorter.

Only flock decides who holds the lock. The identity is just for diagnostics, and `_read_holder` already handles an empty or partly written file by returning None, which `LockHeld` reports as 'identity not yet written'. The message itself says the behavior is tested and harmless. Reordering the calls would make the window shorter, not remove it, and it fixes no incorrect runtime behavior. This is a small hardening idea, not a behavior gap.

- chupa/lockfile.py:65-66 calls os.ftruncate(fd, 0) and then os.pwrite(identity)
- chupa/lockfile.py:82-87 has `_read_holder` comment on the race and return None for empty or invalid content
- chupa/lockfile.py:23 has `LockHeld` print 'unknown holder (identity not yet written)' when holder is None
- chupa/lockfile.py:3 says correctness comes from flock alone

Message: box-000021-493fc784
