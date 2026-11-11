---
id: declined-box-000411-3ba0ed6d
kind: declined
link: box-000411-3ba0ed6d
reopen_after_days: 30
---
The operator proposes removing chupa's per-call cost accounting: the provider `est_cost_per_call_usd` estimate, adapter `reports_cost`, the USD read from the provider stream, the spend total in status, and the `budget_usd` / `--max-budget-usd` eval budgets. The stated reasons are that the operator does not use spend figures and that local providers must declare a meaningless `est_cost_per_call_usd: 0`.

This is a removal and cleanup driven by preference. It names no reachable incorrect runtime behavior. When a non-cost-reporting provider has no estimate, the code refuses at setup with a paved road (`chupa/providers.py:283-284`, `chupa/watchdog.py:72-73`). That is a required config field, not a failure. Declaring `0` works, and the qwen guide already says so (`chupa/docs/host-qwen.md:61`). The suggestion cites no run that failed, stalled, or was refused because of cost accounting. It also cites no wrong decision based on the spend total. No open ticket or registry record covers this removal, so it is not a tombstone. Reopen if evidence shows cost accounting causing incorrect behavior: a call refused or under-run by the `budget_usd` gate (`chupa/providers.py:308-309`), a run ending `infra_error` on a missing estimate after setup passed, or an operator decision misled by the spend figure. The operator can also bypass triage by authoring the removal directly as a ticket.

- chupa/providers.py:283-284 refuses setup with a paved road when a non-cost-reporting provider has no est_cost_per_call_usd; this is a config requirement, not a runtime fault
- chupa/config.py:74 accepts est_cost_per_call_usd >= 0, so `0` is a valid declaration for local providers
- chupa/docs/host-qwen.md:61 already documents `est_cost_per_call_usd: 0` for qwen
- the message reports no failed, refused, or misrouted run caused by budget_usd, --max-budget-usd, or the status spend total
- no open ticket or decision record proposes removing cost accounting

Message: box-000411-3ba0ed6d
