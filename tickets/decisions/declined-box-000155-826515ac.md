---
id: declined-box-000155-826515ac
kind: declined
link: box-000155-826515ac
reopen_after_days: 60
---
The note asks for a drain test that runs the real Merge stage, squashes a `chupa/**` change, and checks that the self-upgrade handoff fires. Today the drain tests use a Script fake that writes its own `commit` field. The note reports no failure. The real Merge stage already journals the field the drain reads.

This only adds a test. It does not show any wrong behavior that can happen at runtime. The real `merge` in `chupa/merge.py:352` journals `{"to": "merged", "commit": commit, "reviewed_sha": reviewed}`. `_Drain._run_one` in `chupa/drain.py:530-533` reads `body.get("commit")` from that same transition and diffs `commit^..commit` against `UPGRADE_PREFIXES`. So the fake and the real stage give the drain the same body shape, and the handoff detection works on real merges. This matches earlier decisions that declined test-only notes (000128, 000131, 000142, 000143).

- chupa/merge.py:352 builds the merged transition body with key `commit` set to the squash SHA (None only for a no-diff settlement)
- chupa/drain.py:530-533 reads body.get('commit'), diffs commit^..commit, and sets self.upgrade when a changed path starts with UPGRADE_PREFIXES
- The note does not report any drain that merged a chupa/** change without handing off

Message: box-000155-826515ac
