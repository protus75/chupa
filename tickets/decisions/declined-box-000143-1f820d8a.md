---
id: declined-box-000143-1f820d8a
kind: declined
link: box-000143-1f820d8a
reopen_after_days: 90
---
Bootstrap suggestion asking for one more drain test: a committed ticket that is modified in the working tree (porcelain `M`) should be skipped until the edit is committed. Today only the untracked-file case is tested. The note reports no failure in which the drain picked up a modified ticket.

This only adds test coverage. The message names no reachable wrong runtime behavior and no incident where the drain dispatched a dirty committed ticket. Under the admission bar, a test-only improvement is declined unless it is tied to a demonstrated harmful behavior gap.

- Message class is `suggestion` from `bootstrap-ingest`, with no stage, outcome or failure report attached.
- The proposal asks only for a new test case for the modified (`M`) porcelain status. It does not claim the drain mishandles that case today.
- Similar test-only bootstrap notes were declined in earlier records: declined-box-000018, -000057, -000128, -000131 and -000142.

Message: box-000143-1f820d8a
