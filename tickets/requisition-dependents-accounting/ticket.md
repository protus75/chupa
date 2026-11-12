---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- lint-requisition-decidable-rules

## Context
- chupa/requisition.py::RequisitionReply
- chupa/requisition.py::review_ticket
- docs/how-chupa-works.md#8. AI providers and prompts
- tests/unit/test_requisition_stage_events.py::test_stage_events

## On-demand
- chupa/specs/requisition_review.md
- tests/integration/test_requisition.py

## Goal / Why
Requisition review receives `coverage_dependents`: test files outside the fence that run fenced code (47-72 files per ticket). The spec lets the reviewer clear the whole list "in the summary with one sentence", and it does. On 2026-11-11, `tests/integration/test_provider_cooldown_failover.py` was on `stage-event-owner-stem`'s list, review cleared every dependent "for one reason", and Implement then failed on exactly that test. The same miss, tests that check behavior and never name the changed symbol, caused retro/9, 11, 28 and 29, and Implement failures on `serve-reoffer-dispatch`, `check-test-timing`, `journal-incremental-read` and `drain-phase-events`. The two prose fixes for this class (`requisition-review-behavioral-closure`, `requisition-review-data-file-consumers`) were rejected on 2026-11-09.

The coverage map also cannot see a test that reads a fenced data or fixture file, because such a test runs no fenced code (`exit-receipt-machinery`, retro/11).

When this ticket is done, the reviewer must account for every dependent in a structured reply field: `fenced`, or `unaffected` with the assertion it read. The engine checks that none were skipped. Tests that mention a fenced non-Python path are added to the list.

## Scope in / Scope out
- In: `chupa/requisition.py`:
  - The dependents list also includes each test file under `tests/` outside the fence whose text contains a fenced path that does not end in `.py`, listed as `<test>: reads <path>`. It is a plain substring scan of the files' text, with no model call. `review_ticket` reads the test sources through a module-level `test_sources(repo)` that lists `(repo / "tests").rglob("*.py")` and returns `{path: text}`, keyed by each file's repo-relative POSIX path, with text from `read_text()`, and calls it only when `## Scope fence` holds at least one path not ending in `.py`. Otherwise the scan touches no disk.
  - `RequisitionReply` gains `dependents`: a list of `{path, status, reason}`. `status` is `fenced` or `unaffected`, and `reason` is non-blank. `dependents` defaults to an empty list (`Field(default_factory=list)`), so a reply that omits it validates and accounts for nothing. For `unaffected`, the reason cites the assertion or input read (`file:line`) and why the change leaves it true.
  - After schema validation, the engine checks the reply's `dependents` paths equal the listed dependents exactly: no path missing, none extra, none twice. Every `fenced` entry must be under a `## Scope fence` prefix. A mismatch is a validation failure that goes back to the model as a retry finding naming each missing, extra or wrongly fenced path, the same way as a JSON shape error.
  - When no coverage map is configured and no data-file consumer is found, `dependents` must be empty.
- In: `chupa/specs/requisition_review.md`: the bullet "Every listed coverage dependent test file must be in the fence or cleared in the summary..." is replaced by the rule above. A dependent the change breaks that is not fenced is still a `snag` finding naming it. The Output format adds `dependents`. A prior review's changed-text limit does not apply to the dependents accounting, which is redone in full on every review. `version` goes one minor step above its value at the base commit.
- In: tests that pin the old wording or version: `tests/unit/test_specs.py` (the version) and `tests/integration/test_requisition.py` (the phrases "in the fence or cleared in the summary" and "An unaccounted file is a `snag` finding naming it", plus its fake replies, which gain `dependents` wherever a coverage map is passed).
- In: `docs/how-chupa-works.md` section 8, the `requisition_review.md` row: dependents are accounted for one by one and include data-file consumers.
- In: new `tests/unit/test_requisition_dependents.py`.
- Out:
  - Engine auto-fencing of a dependent that Implement trips on.
  - Re-review of the rest of the fence closure beyond the dependents.
  - The coverage map builder.

## Scope fence
- chupa/requisition.py
- chupa/specs/requisition_review.md
- docs/how-chupa-works.md
- tests/unit/test_specs.py
- tests/unit/test_requisition_dependents.py
- tests/integration/test_requisition.py

## Acceptance criteria
1. `tests/unit/test_requisition_dependents.py`, driving the dependents check with no disk or provider access:
   - A reply listing every dependent passes.
   - A reply missing one dependent fails, with a retry finding naming that path, not an approve.
   - A reply listing a path that is not a dependent fails, naming it.
   - A reply marking an out-of-fence dependent `fenced` fails, naming it.
   - A reply with an `unaffected` entry whose `reason` is blank fails schema validation.
   - A reply without `dependents` validates, and passes the check when the dependents list is empty.
2. `tests/unit/test_requisition_dependents.py`: with a fence holding `hosts/fixture/data.json` and an in-memory listing of test sources where `tests/integration/test_a.py` contains that path and `tests/integration/test_b.py` does not, the dependents list holds `tests/integration/test_a.py: reads hosts/fixture/data.json` and not `test_b.py`.
3. `tests/integration/test_requisition.py`, through `review_ticket` with a `FakeLLM` and a coverage map listing two dependents: a first reply accounting for only one of them is retried with a finding naming the missing one, and a second, complete reply is accepted.
4. `tests/unit/test_requisition_dependents.py` drives `review_ticket` with monkeypatched `llm_call`, `review_target`, `_base_render`, `load_spec`, `render` and `test_sources`, as `tests/unit/test_requisition_stage_events.py` does, with a coverage map listing one dependent: a first reply omitting it and a second complete reply give two `llm_call` calls, the second carrying a retry finding naming the missing path. With a fence holding only `.py` paths, `review_ticket` never calls `test_sources`. With a fence holding `hosts/fixture/data.json` and a monkeypatched `test_sources` returning one out-of-fence test whose text contains that path, the rendered `coverage_dependents` includes `<test>: reads hosts/fixture/data.json`, and a reply omitting that test is retried with a finding naming it. `test_sources` itself, run against an in-memory fake path object that supports `/`, `rglob`, `relative_to` and `read_text`, returns the fake files' texts keyed by repo-relative path, with no disk access.
5. `tests/unit/test_specs.py` pins `requisition_review` one minor step above its version at the base commit, and the spec no longer contains "cleared in the summary with one sentence".
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- A reply that omits a listed dependent can be accepted.
- The data-file consumer scan calls a model or a subprocess.
- The dependents accounting is limited to the text changed since a prior review.

## Time budget
- expected: 45m
- stuck: 90m
