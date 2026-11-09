---
id: declined-box-000222-74e506c6
kind: declined
link: box-000222-74e506c6
reopen_after_days: 30
---
The Claude CLI now accepts `--effort <level>`, but `ClaudeAdapter.argv` in `chupa/providers.py` (line 444) ignores the effort value and only records it in provenance. The note asks whether to pass effort through to the CLI and to update the plan text in section 0, prompt 1.

This is a capability gap, not shown incorrect runtime behavior. Claude calls run at the CLI's default effort, and nothing ties that to a failed, slow or wrong run, so there is no harmful result that one ticket could measurably fix. CHUPA_PLAN.md is frozen and is never edited, so the plan-wording half cannot be done. Choosing to escalate Claude effort is a policy and preference decision until evidence shows that Claude surfaces fail or underperform because their effort is ignored.

- chupa/providers.py:444 ClaudeAdapter.argv comment: 'No effort flag: effort is recorded in provenance only.'
- chupa/providers.py:474 CodexAdapter passes effort via model_reasoning_effort, so effort plumbing exists for codex only
- CLAUDE.md: CHUPA_PLAN.md is a frozen bootstrap design record and is never edited
- No failure_report or retro finding links Claude-routed review/author/triage failures to the default effort

Message: box-000222-74e506c6
