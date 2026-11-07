---
id: declined-box-000060-fa95ac64
kind: declined
link: box-000060-fa95ac64
reopen_after_days: 90
---
A bootstrap note asks to add `--verbose` to the Claude CLI argv in section 0, prompt 1 of the frozen plan. `claude -p --output-format stream-json` will not run without `--verbose`, and the provider adapter already passes it. The plan text leaves it out.

The runtime already works: `chupa/providers.py:446` puts `--verbose` in the Claude argv, and line 444 has a comment saying why. The only gap is wording in `CHUPA_PLAN.md`, which is a frozen bootstrap record that tickets never edit. The plan is no longer used to regenerate code (see the merged tickets remove-seeding and prompts-drop-plan). No runtime behavior is wrong.

- chupa/providers.py:446 returns [binary, '-p', '--output-format', 'stream-json', '--verbose', '--model', model, *grant]
- chupa/providers.py:444 comment: stream-json under -p requires --verbose
- CLAUDE.md: CHUPA_PLAN.md is a frozen bootstrap design record and is never edited
- Registry declined-box-000050-42b264ae declined a similar plan-only wording request

Message: box-000060-fa95ac64
