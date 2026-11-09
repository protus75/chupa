---
id: declined-box-000106-9bed5fc5
kind: declined
link: box-000106-9bed5fc5
reopen_after_days: 90
---
A bootstrap note makes two points. First, a stage's `attempt` number, which names its spool directory and its ticket-plane commit key, is the run sequence, so a ticket's first run spools under `0`. Second, `eval/harness.py` has its own `_findings_text` function, which renders findings the same way as `chupa.stages.findings_text` and could import that helper the next time the file is edited.

The first point only describes how attempt numbering works and reports nothing wrong. Registry record declined-box-000081-60090cff already declined the related question of what `<attempt>` means. The second point is a duplicate-code cleanup in the eval harness. The two copies currently render findings identically, so no runtime behavior is wrong, and the note itself defers the change to 'next time it is touched'. Neither point shows a current, materially harmful behavior gap.

- The message says the eval harness copy renders findings the same way as `chupa.stages.findings_text`, so the two outputs do not differ today.
- Spooling the first run under `0` is presented as how the code works, not as a fault.
- declined-box-000081-60090cff already declined the related request to define `<attempt>` versus `<run_seq>` for ticket runs.
- The eval harness is a tool for measuring prompts, not the engine's runtime path, so the duplicate cannot cause a ticket run to fail.

Message: box-000106-9bed5fc5
