---
id: tombstone-box-000200-a63edef9
kind: tombstone
link: declined-box-000015-14c41885
reopen_after_days: 180
---
A bootstrap note says the git operation list in the frozen plan's prompt 5 (section 0) is only part of the list in section 10. Section 10 also names `diff`, `diff --name-only` and `restore`. `chupa/git.py` follows section 10. The note suggests that prompt 5 point to section 10 instead of repeating part of the list.

This is the same request as registry record declined-box-000015-14c41885: the same prompt-5-vs-section-10 git op mismatch and the same proposal to refer to section 10. It also asks for an edit to the wording of the frozen plan and shows no wrong runtime behavior. `CHUPA_PLAN.md` is frozen and is never edited.

- Registry record declined-box-000015-14c41885 already covers this mismatch, which concerns the git op subset in prompt 5 and section 10's `diff`/`diff --name-only`/`restore`.
- The message says git.py already follows section 10, so the runtime is correct.
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.

Message: box-000200-a63edef9
