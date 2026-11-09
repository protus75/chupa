---
id: tombstone-box-000341-50db7662
kind: tombstone
link: requisition-coverage-dependents
reopen_after_days: 30
---
The suggestion asks that whoever writes a ticket's Coverage clearance first check every test file the coverage map lists as a dependent of the changed source files. On 2026-11-07, serve-reoffer-dispatch drafts at first left out the soak, reliability-battery and watchdog-activation tests. Merged ticket requisition-coverage-dependents already does this check: before review it works out the out-of-fence coverage dependents, gives them to requisition review, and the review snags any listed dependent that is neither fenced nor cleared.

This repeats the merged requisition-coverage-dependents ticket. Its Task rule in chupa/specs/requisition_review.md says every listed coverage dependent must be fenced or cleared with a reason, and an unaccounted file is a snag. In the serve-reoffer-dispatch incident the gap was closed before merge. The ticket was revised several times on 2026-11-07, after requisition-coverage-dependents was written. Its final version fences test_daemon_soak, test_daemon_soak_runner, test_reliability_battery and test_watchdog_activation and merged. No harmful runtime behavior remains that would need a separate rule on the authoring side.

- chupa/specs/requisition_review.md:26: every listed coverage dependent test file must be in the fence or cleared in the summary; an unaccounted file is a snag
- docs/how-chupa-works.md:581: requisition_review checks coverage dependents outside the fence and snags on a missing or invalid map
- git log: requisition-coverage-dependents ticket commits end 2026-11-07 00:28; serve-reoffer-dispatch was revised 03:18-09:57 the same day
- tickets/serve-reoffer-dispatch/ticket.md:70-78: final Coverage clearance names and fences test_daemon_soak, test_daemon_soak_runner, test_reliability_battery and test_watchdog_activation; stem is merged

Message: box-000341-50db7662
