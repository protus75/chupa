---
id: tombstone-box-000294-f42a6754
kind: tombstone
link: requisition-coverage-dependents
reopen_after_days: 30
---
On 2026-10-10 requisition review approved supervised-merge-hold even though its Verification required tests/test_daemon_composition.py to stay green, and that file was outside the fence. One assertion in that file pins a single Effect completion, but the required merge-regate receipt adds a second. Implement bounced premise_failed before writing any code. The finding asks the review spec to trace out-of-fence preservation suites whose assertions the Scope-in change contradicts.

The incident happened before requisition-coverage-dependents merged (2026-11-07). That ticket fixed this class of miss. Requisition review now gets a mechanically computed list of test files outside the fence that run fenced code. The spec makes each one a snag unless it is fenced or cleared with a sentence explaining why the change does not affect it. tests/test_daemon_composition.py runs the fenced chupa/mergequeue.py through test_composed_merge_queue_admits_reviewed_candidate, so the review would now have to fence that suite or justify leaving it out. The remaining part of the request, tracing preservation suites named in Verification by their assertions, is the same gap described in different words. It also carries the overcorrection risk the finding names itself. No incident after 2026-11-07 shows the coverage-dependents rule missing such a file.

- tickets/supervised-merge-hold history: the premise_failed harvest and diagnosis were committed 2026-10-10, and a later commit fenced tests/test_daemon_composition.py; the ticket is now merged.
- Commit 11b291e9 (requisition-coverage-dependents) is dated 2026-11-07, after the incident.
- chupa/specs/requisition_review.md line 26: every listed coverage dependent test file must be in the fence or cleared in the summary with one sentence; an unaccounted file is a snag.
- chupa/specs/requisition_review.md lines 58-62 feed coverage_dependents ('Test files outside the fence that run fenced files') to the reviewer.
- The supervised-merge-hold fence held chupa/mergequeue.py, and the contradicted test exercises the composed merge queue.

Message: box-000294-f42a6754
