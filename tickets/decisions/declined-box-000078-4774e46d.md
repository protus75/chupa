---
id: declined-box-000078-4774e46d
kind: declined
link: box-000078-4774e46d
reopen_after_days: 60
---
The review eval runs fixtures through the shared Driver, which takes `caps.retry` as its schema re-prompt cap. If a reviewer keeps returning invalid JSON on one fixture, that fixture can cost up to retry+1 opus calls (7 with the shipped value of 6). The note suggests giving the eval its own lower cap once a flat per-run USD cap exists.

This is about possible cost, not something that has gone wrong. No eval run or journal record shows a fixture using up its re-prompt cap. The worst case is limited by configuration: `caps.retry` is set in `config.yaml`, and `chupa/config.py` requires it to be at or below `caps.diagnosis`. The note ties the change to a Phase 6 per-run USD cap, which is not a current ticket. A separate eval cap would be a new config setting with no incident to justify it, and the engine rules forbid that. Registry record declined-box-000041 already declined a related request to share the `caps.retry` budget, for the same reason.

- chupa/driver.py:176 sets retry_cap=config.caps.retry each time a Driver is built, so eval runs use the same cap as every other stage run
- chupa/config.py:467-471 refuses a config where caps.retry is above caps.diagnosis, so the worst case has a configured ceiling
- No open ticket, merged stem, or registry record reports an eval fixture using up its schema re-prompts or overspending
- declined-box-000041-605fce3c declined a related retry-budget hardening because there was no observed harm

Message: box-000078-4774e46d
