---
id: declined-box-000372-aff81070
kind: declined
link: box-000372-aff81070
reopen_after_days: 30
---
The note says `chupa/git.py` has no operation that returns a committed file's exact bytes. It reports that `committed_core` in `chupa/hostfiles.py` hashes blobs itself and calls the private `Git._run`, and that this caused a `premise_failed` bounce on core-drift-preflight. It proposes adding a byte-returning git seam.

The note shows no runtime behavior that is wrong today. `committed_core` reads the bytes in the worktree and accepts them only when their hash matches `rev_parse(HEAD:<path>)`. That check is correct, just written by hand. Calling `Git._run` directly is a pattern used across the engine (stages, merge, retro, triage, serve, daemon, runner), so a new seam would be a refactor, not a fix. The real harm in the note is the paid `premise_bounce` on core-drift-preflight. The open ticket diagnose-spec-reachable-road-rule already covers that: Implement treated the missing seam in the out-of-fence `git.py` as a fence wall, even though a road inside the fence existed (`Path.read_bytes()` plus a blob-id check), and that road is what shipped.

- chupa/hostfiles.py:491-519 committed_core reads HEAD:chupa/hostfiles.py via git._run("show") and checks conduct files against git.rev_parse(HEAD:<rel>) blob ids
- git._run is called directly in chupa/stages.py, merge.py, mergequeue.py, retro.py, triage.py, serve.py, daemon.py, runner.py, rework.py, author.py, tickets.py, __main__.py
- Open ticket diagnose-spec-reachable-road-rule covers the core-drift-preflight attempt-7 premise_failed bounce on the git.py/seams.py fence wall
- Registry tombstone-box-000292-782578ef links the same bounce to diagnose-spec-reachable-road-rule

Message: box-000372-aff81070
