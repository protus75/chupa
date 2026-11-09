---
id: declined-box-000227-6bbad4ab
kind: declined
link: box-000227-6bbad4ab
reopen_after_days: 90
---
A bootstrap note says each eval fixture case is a directory with three files (`ticket.md`, `diff.patch`, `expected.json`). Section 7 of the frozen plan says an eval case is one closed envelope file. The note warns that a GO-grade set of 65 or more cases would come to about 195 files, well over the 30-file diff budget. It asks for one envelope file per case before `go-grade-machinery` grows the set.

Registry record declined-box-000073-6497ff4 already decided this same concern: the eval fixture directory layout against the plan's one-envelope-file rule and the roughly 195-file count against the 30-file budget. In addition, `go-grade-machinery` and `go-grade-run` have both merged, and the note shows no current runtime harm.

- declined-box-000073-a6497ff4 describes the same fixture-layout mismatch, the same ~195-file estimate and the same request to reconcile before go-grade-machinery
- go-grade-machinery and go-grade-run are in the merged list, so the set this note wanted to get ahead of has already grown
- The note's only harm is a mismatch between plan wording and the fixture layout. CHUPA_PLAN.md is frozen and is never edited
- unresolvable link: declined-box-000073-a6497ff4

Message: box-000227-6bbad4ab
