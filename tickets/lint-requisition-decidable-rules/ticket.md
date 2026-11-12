---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/tickets.py::validate_ticket
- chupa/tickets.py::_regression
- chupa/covgate.py::parse_gate
- chupa/requisition.py::review_ticket
- chupa/requisition.py::review_target
- chupa/__main__.py::_lint
- docs/how-chupa-works.md#3. Tickets

## On-demand
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py
- tests/integration/test_requisition.py

## Goal / Why
Requisition review keeps missing ticket defects that a program can decide from the ticket text and the repo alone. Each was added to `chupa/specs/requisition_review.md` as a prose bullet after the misses that earned it, and the misses kept coming, or became repeated snag rounds:

- `## Regression` running `./dev.py test` or pytest instead of a carried reproducer: retro/30 and retro/35 (shared-hold-rule, drain-ceiling-carried-on-handoff).
- A `carries:` reproducer outside `## Scope fence`: same retros.
- A fenced file with a unit coverage floor and no fenced `tests/unit` file: retro/33 (results-schema-2-reader, core-drift-preflight, review-lock-only-for-intake). On 2026-11-11 it also took snag rounds on `retro-reemit-skip` and `retro-finding-recurrence`.

The one rule already moved from prose to lint, that `carries:` must be a test or fixture path (dc226617, `chupa/tickets.py::_regression`), has had no miss since.

When this ticket is done, these three rules are lint findings. `chupa lint`, `chupa new` and intake report them with a paved road before any model call, and the requisition spec drops the prose that duplicated them.

## Scope in / Scope out
- In: a new function `lint_findings(ticket, repo)` in `chupa/tickets.py` that returns the three findings below for a parsed ticket. Only intake, the `lint` and `new` verbs (`chupa/__main__.py`) and requisition's `review_target` call it; `review_target` raises `TicketInvalid` with its findings. `validate_ticket`, `parse_ticket` and their other callers (merge gate, merge queue, `run`, `review`, `order`, Author, rework) are unchanged, so an already approved ticket never fails these rules at merge or in retro recovery. It adds:
  - Regression runs a carried file: the `## Regression` command names a path under one of its `carries:` prefixes. Otherwise there is a finding with the road "run a reproducer under a `carries:` prefix; a test runner such as `./dev.py test` or pytest does not speak the regression protocol". This is an allowlist; there is no list of banned runners.
  - Carried files are fenced: every `carries:` prefix is under a `## Scope fence` prefix (the same path matching as the fence). Otherwise there is a finding naming the prefix.
  - Floored files have a unit test: when `<repo>/test-gate.toml` exists and lists a `## Scope fence` path under `[coverage.files]` with a floor above 0, the fence must hold at least one path under `tests/unit/`. Otherwise there is a finding naming the file and its floor. It reads `<repo>/test-gate.toml` with `chupa/covgate.py::parse_gate`. A `GateInvalid` becomes one finding naming `test-gate.toml`; nothing raises. Without a gate file the rule is silent.
- In: `chupa/requisition.py::review_ticket`: a `TicketInvalid` from `review_target` becomes a `snag` verdict carrying those findings, with no model call. An already committed ticket that breaks a new rule is parked at requisition like any other snag, and never crashes the drain.
- In: `chupa/specs/requisition_review.md`: cut the `test-gate.toml` floor bullet down to what lint cannot decide: the fenced `tests/unit` file's named tests run the new lines in each floored file. Cut the Regression bullet down to what lint cannot decide: the reproducer prints only the one-key JSON object, `pass` with exit 0 at head and `defect` with nonzero exit at base, using only code that exists at base. `version` goes one minor step above its value at the base commit.
- In: `tests/unit/test_specs.py` (the `requisition_review` version pin, and the Regression phrases it asserts) and `tests/integration/test_requisition.py::test_spec_loads_and_names_finding_keys` (the floor-bullet phrase) follow the spec text.
- In: the bug-ticket fixtures in `tests/integration/test_tickets.py`, `tests/integration/test_lint_verb.py` and `tests/integration/test_author.py` fence their carried prefixes and run a carried file; each test keeps its original assertion.
- In: `tests/unit/test_requisition_stage_events.py` gains the unit test for the new `review_ticket` branch.
- In: `tests/unit/test_docs_verb.py::test_new_guide_paths_without_disk` and `tests/unit/test_git_commit.py::test_intake_skips_concurrent_commit` stub `lint_findings` to return `[]`, the same way each already stubs `evidence_findings`. Each test keeps its original assertions.
- In: `chupa/docs/host-authoring.md` (Regression and Scope fence guidance) and `docs/how-chupa-works.md` section 3 (ticket lint) say lint now checks these three rules.
- In: new `tests/unit/test_ticket_lint_rules.py`.
- Out:
  - Rules that need judgment: reference closure, behavioral closure, contradictions, and coverage dependents (ticket `requisition-dependents-accounting`).
  - Re-linting committed tickets during the drain's scan.
  - Adding the three rules to `validate_ticket` or to its other callers.
  - Coverage gate behavior.

## Scope fence
- chupa/tickets.py
- chupa/requisition.py
- chupa/__main__.py
- chupa/specs/requisition_review.md
- chupa/docs/host-authoring.md
- docs/how-chupa-works.md
- tests/unit/test_specs.py
- tests/unit/test_ticket_lint_rules.py
- tests/unit/test_requisition_stage_events.py
- tests/integration/test_requisition.py
- tests/integration/test_tickets.py
- tests/integration/test_lint_verb.py
- tests/integration/test_author.py
- tests/unit/test_docs_verb.py
- tests/unit/test_git_commit.py

## Acceptance criteria
1. `tests/unit/test_ticket_lint_rules.py`, calling `lint_findings` on tickets parsed in a temporary repo with no process access:
   - A bug ticket whose Regression command is `./dev.py test tests/x.py` with `carries: tests/regress_x.py` gets the regression-runs-a-carried-file finding. `uv run python tests/regress_x.py` with the same carries gets none.
   - `carries: tests/regress_x.py` with a fence of only `chupa/x.py` gets the carried-files-fenced finding naming `tests/regress_x.py`. With `tests/regress_x.py` added to the fence, there is none.
   - With a `test-gate.toml` listing `"chupa/x.py" = 12` under `[coverage.files]`, a fence of `chupa/x.py` alone gets the floor finding naming `chupa/x.py` and `12`. Adding `tests/unit/test_x.py` clears it. A floor of `0`, or no `test-gate.toml`, gives no finding.
   - A malformed `test-gate.toml` gives one finding naming `test-gate.toml` and raises nothing.
   - `parse_ticket` and `validate_ticket` on the first failing text raise none of the three findings, so the drain's scan and the merge gate are unchanged.
   - The `lint` verb, run in-process on the first failing ticket, prints the regression-runs-a-carried-file finding.
2. `tests/integration/test_requisition.py`: `review_ticket` on a committed ticket that breaks one of the rules returns `verdict` `snag` carrying the lint finding, makes no provider call (the `FakeLLM` holds no reply), and raises nothing. `tests/unit/test_requisition_stage_events.py` has a test that patches `requisition.review_target` to raise `TicketInvalid` and asserts a `snag` verdict carrying that finding with zero `llm_call` invocations.
3. `tests/unit/test_specs.py` pins `requisition_review` one minor step above its version at the base commit. The spec's Task no longer contains "the fence must hold a `tests/unit` file" or "under both a `- carries:` path prefix", and `test_spec_loads_and_names_finding_keys` asserts the shortened floor bullet's phrase.
4. `./dev.py lint` over every unsettled ticket in this repo at the branch head reports no finding from the three new rules, or the run record names each finding as a real defect in that ticket.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- A rule is enforced by a denylist of runner names instead of requiring a carried path.
- A committed ticket that breaks a new rule crashes the drain or is dropped from the queue silently.
- The requisition spec keeps prose that duplicates a rule lint now enforces.
- `lint_findings` accepts a value that is not a parsed `Ticket`, so that a test's fake passes.

## Time budget
- expected: 45m
- stuck: 90m
