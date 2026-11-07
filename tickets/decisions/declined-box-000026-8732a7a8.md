---
id: declined-box-000026-8732a7a8
kind: declined
link: box-000026-8732a7a8
reopen_after_days: 90
---
The config loader runs its cross-key checks only after pydantic schema validation passes. These checks cover API refusal, routing names an existing provider, and retry not above diagnosis. So if a config has both a type error and a cross-key error, the operator sees only the type error on the first load and finds the second after fixing it. Both errors still stop the config from loading.

This is a preference about how errors are reported, not a harmful behavior gap. The loader already refuses every invalid config, and the note itself says that is fine. Showing errors one load at a time costs an extra fix-and-reload, but it never lets a bad config through or makes the engine behave wrongly. No incident shows an operator was hurt by the order. No open ticket, merged ticket, or registry decision covers this, so it is not a tombstone.

- The message is a bootstrap-ingest suggestion that calls the current behavior 'Fine for fail-closed' and asks only to note it if operators want all findings at once.
- No failure report, stage, or outcome is attached, so nothing shows a runtime failure.
- Related config decisions (decision-box-000022, -000024, -000025) deal with spec wording and seam use, not the order errors are reported in.

Message: box-000026-8732a7a8
