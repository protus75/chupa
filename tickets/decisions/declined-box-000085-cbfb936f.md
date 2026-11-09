---
id: declined-box-000085-cbfb936f
kind: declined
link: box-000085-cbfb936f
reopen_after_days: 90
---
Intake does not re-check the `source` field when an established ticket is edited: it compares nothing against the committed version. The note asks for a git `show <rev>:<path>` operation so intake could refuse an edit that changes `source: seed` to `human`.

The gap is real: `_intake_claims` in chupa/tickets.py returns early for a stem that already exists and never reads the committed frontmatter. No harmful behavior follows from it. Seeding has been removed (merged `remove-seeding`, `remove-bootstrap-ingest`), so the engine no longer creates `seed` tickets. No engine code branches on `source == "seed"`. The only `source` checks look for `box:bug_report` and `box:retro_finding` (triage.py:228, author.py:174, merge.py:215, stages.py:1335). Changing seed to human therefore changes no scheduling, gate, or merge decision. This is speculative hardening of a check that protects nothing today.

- chupa/tickets.py:625-627: an established stem returns early and keeps its source without comparing against HEAD
- No grep hit for `source == "seed"` in chupa/; source consumers check only `box:bug_report` and `box:retro_finding`
- Merged stems include remove-seeding and remove-bootstrap-ingest

Message: box-000085-cbfb936f
