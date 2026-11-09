---
id: tombstone-box-000300-868b5f24
kind: tombstone
link: declined-box-000299-84e19a9f
reopen_after_days: 30
---
The report says four tests in tests/test_seeded_phase7_core.py failed on base fa8f5a54 because the retired tickets/phase7-continue/ticket.md was missing. Registry record 000299 already decided this same report. On current main that test module is gone, so the failure no longer happens.

This is the same report as declined-box-000299-84e19a9f: the same test file, the same missing retired ticket and the same four failures. That record found that commit acf9f661 removed the test file and that no tracked test refers to phase7-continue. Checking the current tree confirms both facts, so the failure cannot happen on main.

- Glob tests/test_seeded_phase7* matches no files on current main
- Grep for 'phase7-continue' under tests/ finds no matches
- Registry record declined-box-000299-84e19a9f records the same four failing tests in tests/test_seeded_phase7_core.py and their removal in commit acf9f661

Message: box-000300-868b5f24
