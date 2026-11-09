---
id: tombstone-box-000334-9b4baf9a
kind: tombstone
link: recent-steps-check-merge
reopen_after_days: 30
---
The note says the mechanical Check stage never shows in the extension's Recent Steps or in watch, because only the LLM Driver writes stage_start/stage_end to engine.log. It asks for Check start/end events so the row appears and opens checks.json. The merged ticket recent-steps-check-merge already made this change.

This repeats merged ticket recent-steps-check-merge. That ticket's Goal names the same gap: only Driver logs stage events, so Check and merge never appear in Recent Steps and every row opens ticket.md. It added check and merge start/end events, and snapshot paths that open checks.json for a Check row. Current code already does all of this, so nothing is left to build.

- tickets/recent-steps-check-merge/ticket.md Goal: 'The engine log gets stage_start/stage_end only from Driver (chupa/driver.py), so the mechanical Check and merge steps never appear.'
- chupa/stages.py:1559 logs stage_start with surface='check' and chupa/stages.py:1587 logs stage_end with surface='check' and the outcome
- chupa/runner.py:207-209 logs stage_start/stage_end with surface='merge'
- chupa/observe.py:20 STEP_NAMES includes check: 'Check'; chupa/observe.py:682 maps check to checks.json for the step path

Message: box-000334-9b4baf9a
