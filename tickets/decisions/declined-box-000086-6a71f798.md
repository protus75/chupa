---
id: declined-box-000086-6a71f798
kind: declined
link: box-000086-6a71f798
reopen_after_days: 90
---
A bootstrap note asked to define an exact closed grammar for the `Exit-read window` ticket section before the first phase-exit seed used one. Phase exits and seeding have since been removed. The engine no longer parses the section, and intake now rejects it as an unknown body section.

The gap no longer exists. Merged tickets remove-phase-exits, remove-seeding and remove-plan-grammar removed the phase-exit seeds that would have declared this window. Nothing in `chupa/` reads `Exit-read window`. `tests/integration/test_tickets.py:206` checks that a ticket containing `## Exit-read window` is refused as an unknown body section. No current runtime behavior is wrong.

- grep for 'exit.read' in chupa/ returns no matches
- tests/integration/test_tickets.py:206 expects '## Exit-read window' to fail intake with 'unknown body section'
- merged stems include remove-phase-exits, remove-seeding, remove-plan-grammar

Message: box-000086-6a71f798
