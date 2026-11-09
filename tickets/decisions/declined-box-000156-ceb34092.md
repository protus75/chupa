---
id: declined-box-000156-ceb34092
kind: declined
link: box-000156-ceb34092
reopen_after_days: 90
---
If the self-upgrade re-exec fails after the drain journals its handoff signal, for example because `uv` is missing, the parent exits 2 with a generic refusal. The journal keeps a `drain_handoff` signal that no child picked up. The note asks for the refusal text to say the merge landed and that running drain again continues.

The note itself calls the orphaned signal harmless to the fold. The merge is already committed and the lock is released before the spawn, so running `drain` again resumes normally and nothing is lost or stuck. What is left is the wording of an error message in a broken-environment edge case (no `uv` on PATH). That is a preference about the message, not a materially harmful runtime behavior, and no incident shows an operator was misled or blocked. Evidence that would reopen this: an operator who misread the refusal and took a harmful action, such as manually reverting the merge, or a fold or scheduler path that does read the orphaned `drain_handoff` signal.

- chupa/drain.py:281-283 journals HANDOFF_SIGNAL, closes the journal, and sets outcome to handoff before the spawn
- chupa/drain.py:284-295 releases the engine lock in the finally block before the re-exec
- chupa/drain.py:298-303 calls reexec.run only after the lock is released; an ExecutableNotFound raised there goes up to main's refusal path (exit 2)
- The message itself says the orphaned drain_handoff signal is harmless to the fold

Message: box-000156-ceb34092
