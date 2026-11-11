---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/tickets.py::parse_ticket
- chupa/tickets.py::validate_ticket
- chupa/tickets.py::evidence_findings
- chupa/tickets.py::missing_evidence_findings
- chupa/author.py::AuthorGate.check
- chupa/drain.py::_Drain._scan
- chupa/runner.py::_admit
- docs/how-chupa-works.md#3.2 Intake
- docs/how-chupa-works.md#5.2 Bug tickets
- chupa/docs/host-authoring.md#Bug tickets
- tests/regress_drain_deadline.py

## On-demand
- chupa/__main__.py
- tests/integration/test_tickets.py
- tests/integration/test_author.py
- tests/integration/test_bug_gate.py
- tests/integration/test_lint_verb.py
- tests/integration/test_cli.py
- tests/integration/test_serve_dispatch.py
- tests/integration/test_host_loop.py

## Goal / Why
`chupa/docs/host-authoring.md` (Bug tickets > Evidence) says a `kind: bug` ticket needs at least one evidence file committed with it "before it runs". Only human intake (`intake` in `chupa/tickets.py`) and `lint` enforce that. The Author stage commits its drafts through its own ticket-plane effect, not intake. `AuthorGate.check` writes evidence only for a host report. The confirm verb (`verdict_locked` in `chupa/runner.py`), the drain scan (`_Drain._scan` via `parse_ticket`), the serve watcher, and `run` admission (`_admit`) all validate the ticket without the evidence check.

On 2026-11-11 the Author stage committed `triage-author-invoked-stale-round-guard`, a `kind: bug` ticket from a plain Suggestion Box message, with no `evidence/` directory. It was confirmed, admitted and fully implemented (all 3420 tests green), and only Check's `bug_evidence` gate refused it. Diagnosis said `reject`, but the drain's machine keep re-offered the unchanged ticket and started a second implement that could not pass either: the evidence path is outside every implement fence. Evidence: `evidence/bug-evidence-incident.txt`.

After this change, a `kind: bug` ticket that is not merged or rejected and has no regular evidence file under `tickets/<stem>/evidence/` fails `parse_ticket` with the existing `missing_evidence_findings` finding. Every reader that validates a committed ticket goes through `parse_ticket`: the drain scan (listed under "invalid committed tickets", never dispatched), the serve watcher, `run`, confirm (through `validate_ticket` in intake) and the Author gate. So such a ticket never reaches Implement, and Author can no longer commit an evidence-less bug draft.

## Scope in / Scope out
- In: `chupa/tickets.py`. At the end of `parse_ticket`, once the grammar is valid and the `Ticket` is built, raise `TicketInvalid` with `evidence_findings(ticket, repo)` when it returns findings (filesystem candidates, `paths=None`). Keep `evidence_findings` and `missing_evidence_findings` as the one source of the finding text. Intake and `lint` keep their existing committable-paths check (the `paths=` call), which still catches a gitignored evidence file that the filesystem check accepts. Do not print the same finding twice from `lint`, `new` or intake: if a caller's separate evidence call becomes unreachable or duplicate, delete it rather than guard it.
- In: `chupa/author.py`, only if the tests show the gate needs it. `AuthorGate.check` already writes host-report evidence before `validate_ticket`, so a host-report bug draft keeps passing. A non-report `kind: bug` draft now fails with the evidence finding. Add no new finding text.
- In: `tests/unit/test_parse_ticket_evidence.py` (new). The hard `unit` coverage gate measures `chupa/tickets.py` from `tests/unit` only. Tests:
  - `test_bug_without_evidence_is_invalid`: `parse_ticket` on a valid `kind: bug` ticket text in a `tmp_path` repo with no `evidence/` raises `TicketInvalid` whose findings include the "has no evidence file" message.
  - `test_bug_with_evidence_parses`: the same text with `tickets/<stem>/evidence/out.txt` present returns a `Ticket`.
  - `test_feature_without_evidence_parses`: `kind: feature` with no evidence returns a `Ticket`.
  - `test_rejected_bug_without_evidence_parses`: `state: rejected` (or `merged`) bug with no evidence returns a `Ticket`.
- In: `tests/regress_bug_evidence_before_dispatch.py` (new), a carried reproducer shaped like `tests/regress_drain_deadline.py`. It runs `pytest.main(["tests/unit/test_parse_ticket_evidence.py", "-k", "without_evidence_is_invalid", "-q", "-p", "no:cacheprovider"])` inside `contextlib.redirect_stdout(sys.stderr)`, then prints exactly one JSON object with only `regression_result` on stdout: `pass` and exit 0 when pytest exits 0, `defect` and exit 1 when pytest exits 1, `error` and exit 2 otherwise.
- In: existing tests that build a `kind: bug` ticket fixture without an evidence file and then parse, scan, run or author it. Add a real evidence file to the fixture; never weaken an assertion. Candidates are the On-demand test files.
- In: documentation. In `docs/how-chupa-works.md` sections 3.2 and 5.2 and in `chupa/docs/host-authoring.md` Bug tickets > Evidence, say that every ticket read (intake, lint, confirm, drain, serve, run, Author) refuses a bug ticket without evidence, not only intake. Keep the settled/rejected exemption.
- Out: the drain's machine keep re-offering a Reject-queue stem whose finding no implement can clear; the diagnose lesson-length overflow; teaching the Author spec to pick `kind: feature` for non-report messages; changes to Check's `bug_evidence` gate.

## Scope fence
- chupa/tickets.py
- chupa/author.py
- chupa/__main__.py
- docs/how-chupa-works.md
- chupa/docs/host-authoring.md
- tests/unit/test_parse_ticket_evidence.py
- tests/regress_bug_evidence_before_dispatch.py
- tests/integration/test_tickets.py
- tests/integration/test_author.py
- tests/integration/test_bug_gate.py
- tests/integration/test_lint_verb.py
- tests/integration/test_cli.py
- tests/integration/test_serve_dispatch.py
- tests/integration/test_host_loop.py

## Acceptance criteria
1. `uv run python tests/regress_bug_evidence_before_dispatch.py` prints `{"regression_result": "pass"}` alone on stdout and exits 0 on the branch head. On the merge base it prints `defect`, not `pass`, because `parse_ticket` accepts an evidence-less bug ticket there.
2. `./dev.py test tests/unit/test_parse_ticket_evidence.py` passes `test_bug_without_evidence_is_invalid`, which asserts `TicketInvalid` with the "has no evidence file" finding, not a returned `Ticket`.
3. `./dev.py test tests/unit/test_parse_ticket_evidence.py` passes `test_bug_with_evidence_parses`, `test_feature_without_evidence_parses` and `test_rejected_bug_without_evidence_parses`. A check that refuses every bug ticket, every ticket, or settled tickets fails one of them.
4. `./dev.py test` exits 0.
5. `docs/how-chupa-works.md` section 5.2 states that a bug ticket without evidence is refused wherever a ticket is read, not only at intake.

## Verification
```
uv run python tests/regress_bug_evidence_before_dispatch.py
./dev.py test tests/unit/test_parse_ticket_evidence.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a second copy of the evidence finding text or check logic is added instead of calling `evidence_findings`;
- a merged or rejected bug ticket without evidence becomes invalid;
- an existing test assertion is weakened or deleted to make a bug fixture pass, instead of the fixture gaining an evidence file;
- the reproducer prints `pass` on the merge base, or prints anything but one JSON object on stdout.

## Time budget
- expected: 45m
- stuck: 100m

## Regression
```
uv run python tests/regress_bug_evidence_before_dispatch.py
```
- carries: tests/regress_bug_evidence_before_dispatch.py
- carries: tests/unit/test_parse_ticket_evidence.py
