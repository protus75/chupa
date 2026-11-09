---
id: tombstone-box-000198-5d6fde71
kind: tombstone
link: declined-box-000011-ceff31a7
reopen_after_days: 90
---
Each `Effects` object loads its set of completed keys from the journal once, when it is created. A second object built over the same journal in the same process does not see keys that the first object completes later. The note asks for one shared `Effects` per session, created alongside the journal.

Registry record declined-box-000011-ceff31a7 already settled this gap. Both name the same problem: the completed-key set is per instance, so instances over one journal diverge. Both propose the same fix: build one `Effects` per session alongside the journal. The new message adds no new evidence and no reachable failure.

- declined-box-000011-ceff31a7: same per-instance completed-key divergence and the same proposal of one shared Effects per session
- declined-box-000126-4e9db96f: runner.bind already makes the Driver share the checkout's journal, so the production path uses one writer handle
- The message reports no observed wrong replay or duplicate effect

Message: box-000198-5d6fde71
