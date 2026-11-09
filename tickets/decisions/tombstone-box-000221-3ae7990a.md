---
id: tombstone-box-000221-3ae7990a
kind: tombstone
link: declined-box-000060-fa95ac64
reopen_after_days: 90
---
The note asks for `--verbose` to be added to the Claude CLI argv in prompt 1 of the frozen plan's section 0, because `claude -p --output-format stream-json` will not run without it. The provider adapter already passes the flag, so only the plan text leaves it out.

Registry record declined-box-000060-fa95ac64 already decided this request. It covered the same missing `--verbose` in the same section 0, prompt 1 argv contract, and noted that the adapter already passes the flag. That earlier decision still holds. `CHUPA_PLAN.md` is a frozen design record that is never edited, and the adapter already sends the flag, so nothing at runtime behaves wrongly.

- Decision registry entry declined-box-000060-fa95ac64 describes the same request: add `--verbose` to the Claude CLI argv in section 0, prompt 1, which the adapter already passes.
- The message says the adapter adds `--verbose`, so the stream-json calls run correctly today.
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.

Message: box-000221-3ae7990a
