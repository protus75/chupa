---
id: declined-box-000121-840b47d6
kind: declined
link: box-000121-840b47d6
reopen_after_days: 30
---
The note says that on a re-run, `lift_outbox` raised GitError when every outbox file matched the copy main already lifted, because `git commit --only` had nothing to commit. Current code already skips those files. `_lift_files` in `chupa/stages.py` drops any outbox file whose bytes equal its canonical copy, and `lift_outbox` returns None when no files remain, so the commit is never attempted.

The fix the note proposes, lifting only files whose bytes differ and returning None when nothing changed, is already in the code. The `lift_outbox` docstring states this rule. The crash path cannot be reached, so no harmful behavior gap remains. The separate concern about lifting only the stage's own artifact is covered by the open ticket outbox-lift-named-artifact-only.

- chupa/stages.py:352 `_lift_files` excludes a file when `c.read_bytes() == p.read_bytes()` for its canonical copy
- chupa/stages.py:492-494 `lift_outbox` returns None when `_lift_files` is empty, before the commit effect
- chupa/stages.py:488-489 docstring: a file byte-equal to its canonical copy is a prior run's artifact and is never lifted
- Open ticket outbox-lift-named-artifact-only covers restricting the lift to engine-named artifacts

Message: box-000121-840b47d6
