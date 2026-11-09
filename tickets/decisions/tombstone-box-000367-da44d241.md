---
id: tombstone-box-000367-da44d241
kind: tombstone
link: implement-spec-run-coverage-gate
reopen_after_days: 30
---
In review-lock-only-for-intake, Diagnose twice told the next Implement attempt to reshape `reconcile.orphans` so it adds no statement or branch and clears the unit coverage floor. In the same window, other diagnoses forbade squeezing statements out to recover coverage. The finding asks `chupa/specs/diagnose.md` to settle which advice is correct for a coverage-floor miss.

The harmful result would be production code restructured to dodge the unit coverage gate. Open ticket implement-spec-run-coverage-gate already closes that path: Implement must run the hard coverage gate after its last edit, fix a floor miss only by adding a test inside the fence or report `premise_failed`, and never restructure production code to dodge coverage. Once that rule is in force, a diagnose lesson asking for restructuring cannot cause the restructuring. What remains is wording in the diagnose spec with no separate harmful runtime effect. The failure class (coverage-floor misses fixed by gaming the metric) and the repair are the same as that open ticket's, so this finding duplicates it.

- Finding: review-lock-only-for-intake diagnoses advised restructuring reconcile.orphans to add no statement or branch so the unit gate passes; the results-schema-2-reader and core-drift-preflight diagnoses forbade squeezing statements out.
- Open ticket implement-spec-run-coverage-gate names review-lock-only-for-intake attempt 0 as one of its incidents and requires: 'a floor miss is fixed only by adding a test inside `## Scope fence`, or reported as `premise_failed` ... Implement never restructures production code to dodge coverage.'
- Merged requisition-review-unit-floor (tombstone-box-000365) already covers the authoring side: fences must let new code reach its unit floor.
- The finding's own overcorrection_risk says a ban could block real simplifications, so the diagnose-side wording alone does not show a separate harm.

Message: box-000367-da44d241
