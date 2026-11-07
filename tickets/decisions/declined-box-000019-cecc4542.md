---
id: declined-box-000019-cecc4542
kind: declined
link: box-000019-cecc4542
reopen_after_days: 90
---
`chupa/lockfile.py` takes its lock with flock on `<state_dir>/chupa.lock`. flock locks the file's inode, not its path. If the lock file or the state directory is deleted and recreated while the lock is held, a second process locks the new file and both believe they hold the lock. The note suggests that after acquiring, the lockfile compare `fstat` on its descriptor with `stat` on the path, and reopen and retry if they differ. It proposes this only for when state-dir cleanup tooling exists.

This is conditional hardening against a deletion that no engine code performs. Engine code only creates and reads `chupa.lock`. Nothing in the package deletes it or the state directory. The refusal message already tells operators never to delete the file. The note itself makes the fix depend on cleanup tooling that has not been built. No incident has been reported of two engines holding the lock at once. Reopen if a feature that deletes or recreates the state dir or lock file lands, or if an incident shows two engines running at the same time with the same state dir.

- Searching `chupa/` for rmtree, unlink and `chupa.lock` finds no code that deletes the lock file or the state directory. `chupa.lock` appears only where `lockfile.py` builds its path and where `doctor.py` and `observe.py` read it.
- The message itself makes the change depend on state-dir cleanup tooling landing in the future.
- No open or merged ticket adds state-dir cleanup tooling.

Message: box-000019-cecc4542
