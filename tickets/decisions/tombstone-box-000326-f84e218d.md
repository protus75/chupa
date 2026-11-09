---
id: tombstone-box-000326-f84e218d
kind: tombstone
link: lint-carries-test-paths
reopen_after_days: 30
---
A retro finding says requisition review approved graph-lane-cleanup even though its Regression section carried an implementation file (`vscode-chupa/media/graph.js`). Check's bug_evidence gate then failed it twice. The proposed repair is a requisition-review snag for any carry that is not a test or fixture path, or a carried reproducer missing from the fence.

Merged ticket lint-carries-test-paths fixes this same incident at an earlier stage. Lint now rejects any `carries:` prefix with no tests/test/fixtures/fixture path component, and lint and the check gate read that set from one shared constant. A ticket like graph-lane-cleanup is now refused at authoring, before requisition review or Implement, and the check uses the gate's own path rule, which is the over-correction safeguard the finding asked for. The retro brings no separate incident for the second half (a carried reproducer missing from the Scope fence). graph-lane-cleanup has since merged carrying `tests/regress_graph_lanes.py`.

- tickets/lint-carries-test-paths/ticket.md:17 cites the same graph-lane-cleanup incident: `carries: vscode-chupa/media/graph.js` passed lint, then failed bug_evidence twice after two full implement runs
- tickets/lint-carries-test-paths/ticket.md:19: lint rejects a `carries:` prefix with no tests/test/fixtures/fixture component, using one constant shared with the gate in chupa/tickets.py
- lint-carries-test-paths and graph-lane-cleanup are both in the merged set
- tickets/graph-lane-cleanup/ticket.md:69 now carries `tests/regress_graph_lanes.py`
- No incident is cited where a carried reproducer was left out of the Scope fence

Message: box-000326-f84e218d
