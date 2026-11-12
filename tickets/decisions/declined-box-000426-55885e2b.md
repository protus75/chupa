---
id: declined-box-000426-55885e2b
kind: declined
link: box-000426-55885e2b
reopen_after_days: 30
---
On 2026-11-11, the Diagnose stage for triage-author-invoked-stale-round-guard attempt 0 used four calls to get one valid reply. Two replies had lessons over the 300-character schema bound (`DIAGNOSIS_LESSON_CHARS` in `chupa/artifacts.py`), and one was not JSON. The note suggests making the limit easier to meet, for example by stating a lower limit or giving an example lesson.

The schema re-prompt loop did its job. The fourth call returned a valid diagnosis, so routing, caps and the ticket's outcome were all correct. The only cost was three extra Diagnose calls in one incident. That is a cost to reduce, not wrong runtime behavior. The proposed fix (a lower stated limit or an example lesson) is spec tuning based on a single run, and the merged ticket diagnose-spec-lesson-length already put this limit in `chupa/specs/diagnose.md` twice (lines 28 and 69). Reopen if a Diagnose call uses up its schema re-prompts on lesson length and gets recorded as a mechanical `abandon-human`, which wrongly sends a stem to the Reject queue. Also reopen if a retro window shows lesson-length rejections across several tickets with a measured call cost.

- chupa/artifacts.py:140 DIAGNOSIS_LESSON_CHARS = 300
- chupa/specs/diagnose.md:28 and :69 state the 300-character lesson limit
- The message says the retry loop recovered on the fourth call, so a valid diagnosis was produced
- Merged ticket diagnose-spec-lesson-length already addressed this limit in the spec

Message: box-000426-55885e2b
