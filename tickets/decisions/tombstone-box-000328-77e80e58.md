---
id: tombstone-box-000328-77e80e58
kind: tombstone
link: set-membership-fence-closure
reopen_after_days: 30
---
A retro finding reports that requisition review approved fences that left out files the change forced, even though those files never name a changed symbol. In one case the fence missed the doc-and-test pair that pins the CLI verb table (stats-command, observe-verbs-host-extension). In another it missed eval and test harnesses that wait on serve's removed triage loop (serve-no-auto-triage). The finding proposes adding two closures to the requisition review spec: an inventory closure for enumerated sets and a behavior closure for removed or changed runtime behavior.

Two open tickets already cover both halves of this proposal. Open ticket set-membership-fence-closure adds the inventory closure to `chupa/specs/requisition_review.md` and the author spec. When Scope in adds, removes, renames or moves a set member (CLI subcommand, path, spec name), it fences the tests and docs that list that set. Its motivating cases are the same failure: parser verbs added without fencing `docs/host-running.md` and its verb-table test. Open ticket requisition-review-behavioral-closure adds the behavior closure to the same spec. When Scope in changes a condition that gates an observable outcome, it fences every test whose assertion would then fail. That is the serve-no-auto-triage case under a different name. The one part not explicitly covered is searching `eval/` as well as `tests/`. That is a small widening of requisition-review-behavioral-closure, not a separate ticket, so the finding duplicates open work and needs no new ticket.

- Open ticket set-membership-fence-closure: requisition review approved order-verb and ask-prompt-verb without fencing `docs/host-running.md`, whose verb table is enforced by the host-running test; after the change the spec traces set-membership changes into tests/ and docs/.
- Open ticket requisition-review-behavioral-closure: adds a behavioral closure to `chupa/specs/requisition_review.md` that fences tests asserting an outcome the changed condition now blocks.
- The message's own cases are the CLI verb-table pin (inventory) and the removal of serve's triage loop (behavior), one case per open ticket.
- The message's overcorrection_risk already says the repair should be dropped if overlapping coverage-dependents work covers these cases.

Message: box-000328-77e80e58
