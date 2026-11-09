---
id: declined-box-000116-f4ed6b34
kind: declined
link: box-000116-f4ed6b34
reopen_after_days: 90
---
In `write_squash` (`chupa/merge.py:325-334`), the `merge --squash` and `commit` run inside the `merge/<stem>/<attempt>` effect, before the effect's completion record and the `to: merged` transition are journaled. If the process dies after the commit lands on main but before that record is written, a replay of the same attempt finds no diff between main and the branch. It then either raises the report-admission ValueError or records `commit: None`. A new attempt would rebase to an empty diff. Nothing in `chupa/reconcile.py` uses the `chupa-ticket` trailer to map the squash commit on main back to its ticket. The note asks for that recovery and for a test that pins this crash point.

The window is real in the current code but has not been observed. No incident, failure report or journal evidence shows a squash landing without its `to: merged` record. The proposal is mainly to pin the crash point in tests, which is test-only hardening. The registry has declined the same kind of unobserved crash-window note before: 000110 (crash window in `lift_outbox`, asked only for a test once reconcile existed), 000090 (crash between the intake commit and its signal) and 000016 (crash between the commit and the state save). For consistency this one is declined too. It would be reopened by an observed run where main holds a `chupa-ticket: <stem>` squash but the journal has no `to: merged` for that stem, or one where a replay of `merge/<stem>/<n>` raised the report-admission ValueError or recorded `commit: None` after a real squash.

- chupa/merge.py:325-334: `squash()` runs `merge_squash` and `commit` inside `effects.run(key=merge/<stem>/<attempt>)`. On replay with no completion record, `diff_names(main, stem)` is empty, so it raises the report-admission ValueError or returns `commit: None`.
- chupa/merge.py:352-354: `to: merged` is appended only after the effect returns.
- chupa/reconcile.py has no squash or `chupa-ticket` trailer recovery. It only journals `abandoned` with a `recovery_alert` for orphaned runs.
- chupa/git.py:143-166: `first_parent_squashes` already parses `chupa-ticket` trailers, but only triage uses it.
- Registry precedent: declined-box-000110, declined-box-000090 and declined-box-000016 each declined an unobserved crash-window note.

Message: box-000116-f4ed6b34
