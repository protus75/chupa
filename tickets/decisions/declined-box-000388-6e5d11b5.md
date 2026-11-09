---
id: declined-box-000388-6e5d11b5
kind: declined
link: box-000388-6e5d11b5
reopen_after_days: 30
---
A retro finding says requisition review keeps catching the same fence defects in two tickets: coverage dependents that were neither fenced nor cleared, coverage-floored source files with no fenced tests/unit file, and a test that pins a changed spec version left outside the fence. It asks for `chupa/specs/author.md` to state these rules too.

Changing the proposed file would not have affected the cited cases. Both tickets, retro-test-measurements and retro-test-proposals, have `source: human`, so people wrote them in chat sessions and the Author stage never ran. `chupa/specs/author.md` only governs Author-stage output. Requisition review did its job: lines 29-30 of `requisition_review.md` caught each defect before merge, and both tickets have since merged. Part of the request already exists: author.md line 18 tells the author to fence every test or fixture that pins a changed name, value, argv or version. The coverage-dependent clearance rule also could not work in Author today, because the Author prompt gets no coverage_dependents input (see the record for 000374). Reopen if an Author-stage ticket (`source: box` or another engine-authored source) is snagged or bounced by requisition review for an unfenced or uncleared coverage dependent or a missing tests/unit file for a floored module.

- tickets/retro-test-measurements/ticket.md:3 and tickets/retro-test-proposals/ticket.md:3: `source: human`, not written by the Author stage
- chupa/specs/requisition_review.md:29-30 already snags uncleared coverage dependents and floored files with no fenced tests/unit file
- chupa/specs/author.md:18 already requires fencing tests that pin a changed name, value, argv, or version
- chupa/specs/author.md has no coverage_dependents input block, so Author cannot see the dependent list (also noted in declined-box-000374-ab00980b)
- retro-test-measurements and retro-test-proposals are both in the merged set

Message: box-000388-6e5d11b5
