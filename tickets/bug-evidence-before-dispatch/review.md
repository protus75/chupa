# Review: snag

The parse_ticket evidence check only exempts settled tickets by their frontmatter state, so intake now refuses edits to bug tickets that the journal marks merged, already_satisfied or rejected but whose frontmatter still says confirmed, and the test that pinned this exemption was changed to include evidence, which hides the break.

## Findings

- [logic] chupa/tickets.py:481 `evidence_findings(ticket, repo)` in `parse_ticket` exempts a ticket only when its frontmatter `state` is merged or rejected. The engine never restamps frontmatter on merge: historical merged bug tickets such as `tickets/retro-window-bound/ticket.md` and `tickets/mergequeue-snapshot-argv/ticket.md` still say `state: confirmed` and have no `evidence/`. `intake` (tickets.py ~line 691) calls `validate_ticket` before its journal-state guard `states.get(stem) not in {"merged", "already_satisfied", "rejected"}`, so an edit to any such ticket is now refused. That guard is now dead for the missing-evidence case. The Definition of rejected forbids this: "a merged or rejected bug ticket without evidence becomes invalid". (do instead: Keep the journal-state exemption reachable in intake inside chupa/tickets.py. For example, run the grammar parse without the evidence check for a stem whose journal state is merged, already_satisfied or rejected, and keep `parse_ticket`'s evidence check for every other read. The check must still call `evidence_findings` and add no second copy of the finding text.)
- [acceptance] tests/integration/test_tickets.py:476 `test_settled_bug_is_not_rejudged_for_evidence` exists to prove that a historical bug without evidence (its commit message says so) is not rejudged at intake when the journal says merged, already_satisfied or rejected. Adding `evidence_file(root)` to every parametrization makes the test vacuous: it now passes whether or not the exemption works. It hides the regression in the `("confirmed", "merged")`, `("confirmed", "already_satisfied")` and `("confirmed", "rejected")` cases. The ticket says to give a fixture evidence only for tests whose subject is not evidence absence, and to never weaken an assertion. (do instead: Remove the added `evidence_file(root)` call from this test and fix intake so the journal-settled cases pass without evidence.)
- [acceptance] docs/how-chupa-works.md:- The updated text says "Settled and rejected tickets are exempt." With this diff that holds only for tickets whose frontmatter state is settled. Intake refuses a journal-settled bug ticket whose frontmatter is still `confirmed`. chupa/docs/host-authoring.md makes the same claim: "Settled and rejected tickets are exempt from the evidence check." (do instead: Restore the journal-state exemption in intake so the documented exemption is true, and keep both docs accurate.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "47588a1b78dc705a1b67297eb7743a619b578884",
  "stem": "bug-evidence-before-dispatch",
  "reviewed_sha": "47588a1b78dc705a1b67297eb7743a619b578884",
  "summary": "The parse_ticket evidence check only exempts settled tickets by their frontmatter state, so intake now refuses edits to bug tickets that the journal marks merged, already_satisfied or rejected but whose frontmatter still says confirmed, and the test that pinned this exemption was changed to include evidence, which hides the break.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/tickets.py",
      "line": 481,
      "message": "`evidence_findings(ticket, repo)` in `parse_ticket` exempts a ticket only when its frontmatter `state` is merged or rejected. The engine never restamps frontmatter on merge: historical merged bug tickets such as `tickets/retro-window-bound/ticket.md` and `tickets/mergequeue-snapshot-argv/ticket.md` still say `state: confirmed` and have no `evidence/`. `intake` (tickets.py ~line 691) calls `validate_ticket` before its journal-state guard `states.get(stem) not in {\"merged\", \"already_satisfied\", \"rejected\"}`, so an edit to any such ticket is now refused. That guard is now dead for the missing-evidence case. The Definition of rejected forbids this: \"a merged or rejected bug ticket without evidence becomes invalid\".",
      "paved_road": "Keep the journal-state exemption reachable in intake inside chupa/tickets.py. For example, run the grammar parse without the evidence check for a stem whose journal state is merged, already_satisfied or rejected, and keep `parse_ticket`'s evidence check for every other read. The check must still call `evidence_findings` and add no second copy of the finding text.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/integration/test_tickets.py",
      "line": 476,
      "message": "`test_settled_bug_is_not_rejudged_for_evidence` exists to prove that a historical bug without evidence (its commit message says so) is not rejudged at intake when the journal says merged, already_satisfied or rejected. Adding `evidence_file(root)` to every parametrization makes the test vacuous: it now passes whether or not the exemption works. It hides the regression in the `(\"confirmed\", \"merged\")`, `(\"confirmed\", \"already_satisfied\")` and `(\"confirmed\", \"rejected\")` cases. The ticket says to give a fixture evidence only for tests whose subject is not evidence absence, and to never weaken an assertion.",
      "paved_road": "Remove the added `evidence_file(root)` call from this test and fix intake so the journal-settled cases pass without evidence.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "The updated text says \"Settled and rejected tickets are exempt.\" With this diff that holds only for tickets whose frontmatter state is settled. Intake refuses a journal-settled bug ticket whose frontmatter is still `confirmed`. chupa/docs/host-authoring.md makes the same claim: \"Settled and rejected tickets are exempt from the evidence check.\"",
      "paved_road": "Restore the journal-state exemption in intake so the documented exemption is true, and keep both docs accurate.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
