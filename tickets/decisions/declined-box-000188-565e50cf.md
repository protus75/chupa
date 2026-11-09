---
id: declined-box-000188-565e50cf
kind: declined
link: box-000188-565e50cf
reopen_after_days: 90
---
A bootstrap seeding note says frozen-plan unit 19.P2 lists four shakeout-report fields (member, planted fault, observed, producing run). The seeded tickets also emit `group`, `expected`, `auditor` and `green` so that battery-green and auditor-green can be read from the committed report. The note asks 19.P2 to pin the full field list.

This asks for a wording change to the frozen plan, which is never edited (`CHUPA_PLAN.md` is a frozen bootstrap record). The shakeout tickets that emit the extra fields have merged (shakeout-runner, shakeout-report-lane and others). The note reports no wrong runtime behavior: nothing says a report reader fails, or that a green verdict is misread, because of the extra or missing fields. Registry records 000185, 000186 and 000187 declined similar plan-wording requests from seeding notes.

- The message asks only to pin the field list in plan unit 19.P2. It cites no failure.
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.
- Merged stems include shakeout-runner, shakeout-report-lane, shakeout-drain, shakeout-merge, shakeout-providers, shakeout-recovery, shakeout-stages and reliability-run.
- Similar seeding plan-wording notes were declined: declined-box-000185-8a46a7b6, declined-box-000186-2077a583, declined-box-000187-b982a3cc.

Message: box-000188-565e50cf
