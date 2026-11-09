---
id: tombstone-box-000292-782578ef
kind: tombstone
link: diagnose-spec-reachable-road-rule
reopen_after_days: 30
---
Implement attempt 7 bounced premise_failed on a fence wall (git.py/seams.py) after trying only the byte-exact blob read, even though an in-fence road existed: gates get the candidate worktree Path, so the bytes can be read with Path.read_bytes(). The retro proposes that implement.md require ruling out every in-fence road, including each alternative a finding states, before calling a fence wall.

This is the same incident and the same harm already captured by open ticket diagnose-spec-reachable-road-rule: attempt 7's needless premise_failed spent a capped premise_bounce when a Path.read_bytes() road inside the fence was available. That ticket names the cause. The attempt-6 diagnosis lesson told implement to report a missing fact if no bytes seam existed, and implement followed it. The fix is to steer the lesson to a stated road that is reachable inside the fence. implement.md already allows a scope bounce only when the criteria 'force' an edit outside the fence, and it requires every forced file to be worked through. Once the misdirecting lesson is fixed, the evidence shows no separate implement-side failure. Adding a second rule on the implement side also carries the overcorrection risk the message itself names: genuine fence-wall bounces could turn into convoluted workarounds.

- Open ticket diagnose-spec-reachable-road-rule Goal: attempt-6 diagnosis said 'use a bytes-returning git.py seam if merged code has one; if it has none, report that missing fact'; attempt 7 returned premise_failed on a fence wall (git.py/seams.py) while Path.read_bytes() through gates.run_gates was reachable in-fence
- chupa/specs/implement.md:57-62 already limits a scope premise_failed to criteria that 'force' an edit outside the fence and requires working through every forced file
- The message's overcorrection_risk warns that an implement-side rule could suppress genuine authoring_error bounces

Message: box-000292-782578ef
