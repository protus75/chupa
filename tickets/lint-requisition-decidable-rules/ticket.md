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
- In: `chupa/tickets.py::validate_ticket` (intake, `chupa lint`, `chupa new` and requisition's `review_target`), not `parse_ticket`, so the drain's scan of already committed tickets is unchanged. It adds:
  - Regression runs a carried file: the `## Regression` command names a path under one of its `carries:` prefixes. Otherwise there is a finding with the road "run a reproducer under a `carries:` prefix; a test runner such as `./dev.py test` or pytest does not speak the regression protocol". This is an allowlist; there is no list of banned runners.
  - Carried files are fenced: every `carries:` prefix is under a `## Scope fence` prefix (the same path matching as the fence). Otherwise there is a finding naming the prefix.
  - Floored files have a unit test: when `<repo>/test-gate.toml` exists and lists a `## Scope fence` path under `[coverage.files]` with a floor above 0, the fence must hold at least one path under `tests/unit/`. Otherwise there is a finding naming the file and its floor. It reads the gate with `chupa/covgate.py::parse_gate`, at the same default path the covgate verb uses. Without a gate file the rule is silent.
- In: `chupa/requisition.py::review_ticket`: a `TicketInvalid` from `review_target` becomes a `snag` verdict carrying those findings, with no model call. An already committed ticket that breaks a new rule is parked at requisition like any other snag, and never crashes the drain.
- In: `chupa/specs/requisition_review.md`: delete the `test-gate.toml` floor bullet. Cut the Regression bullet down to what lint cannot decide: the reproducer prints only the one-key JSON object, `pass` with exit 0 at head and `defect` with nonzero exit at base, using only code that exists at base. `version` goes from `3.9` to `3.10`.
- In: `tests/unit/test_specs.py` (the `3.9` pin, and the Regression phrases it asserts) and `tests/integration/test_requisition.py::test_spec_loads_and_names_finding_keys` (the floor-bullet phrase) follow the spec text.
- In: `chupa/docs/host-authoring.md` (Regression and Scope fence guidance) and `docs/how-chupa-works.md` section 3 (ticket lint) say lint now checks these three rules.
- In: new `tests/unit/test_ticket_lint_rules.py`.
- Out:
  - Rules that need judgment: reference closure, behavioral closure, contradictions, and coverage dependents (ticket `requisition-dependents-accounting`).
  - Re-linting committed tickets during the drain's scan.
  - Coverage gate behavior.

## Scope fence
- chupa/tickets.py
- chupa/requisition.py
- chupa/specs/requisition_review.md
- chupa/docs/host-authoring.md
- docs/how-chupa-works.md
- tests/unit/test_specs.py
- tests/unit/test_ticket_lint_rules.py
- tests/integration/test_requisition.py

## Acceptance criteria
1. `tests/unit/test_ticket_lint_rules.py`, calling `validate_ticket` on ticket text in a temporary repo with no process access:
   - A bug ticket whose Regression command is `./dev.py test tests/x.py` with `carries: tests/regress_x.py` gets the regression-runs-a-carried-file finding. `uv run python tests/regress_x.py` with the same carries gets none.
   - `carries: tests/regress_x.py` with a fence of only `chupa/x.py` gets the carried-files-fenced finding naming `tests/regress_x.py`. With `tests/regress_x.py` added to the fence, there is none.
   - With a `test-gate.toml` listing `"chupa/x.py" = 12` under `[coverage.files]`, a fence of `chupa/x.py` alone gets the floor finding naming `chupa/x.py` and `12`. Adding `tests/unit/test_x.py` clears it. A floor of `0`, or no `test-gate.toml`, gives no finding.
   - `parse_ticket` on the first failing text raises none of the three findings, so the drain's scan is unchanged.
2. `tests/integration/test_requisition.py`: `review_ticket` on a committed ticket that breaks one of the rules returns `verdict` `snag` carrying the lint finding, makes no provider call (the `FakeLLM` holds no reply), and raises nothing.
3. `tests/unit/test_specs.py` pins `requisition_review` at `3.10`, and the spec's Task no longer contains the `test-gate.toml` floor bullet or the "under both a `- carries:` path prefix" wording.
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

## Time budget
- expected: 45m
- stuck: 90m
