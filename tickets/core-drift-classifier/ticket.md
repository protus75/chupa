---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase5-exit
- core-renderer

## Context
- chupa/gates.py
- chupa/merge.py
- chupa/stages.py
- chupa/seams.py
- chupa/specs.py

## Plan contract
- 19.I
- 19.P6.core-drift-classifier
- 19.P6.core-renderer
- section 8

## Goal / Why
Direct byte classification distinguishes managed-block drift and forbidden project process rules without effects.

## Scope in / Scope out
Implement only the classifier row in the renderer-owned chupa/hostfiles.py and its tests/test_hostfiles.py. Both files are sibling creations in this admission, so they are read after the renderer merges and are excluded from authoring Context. Reuse that parser and fresh branch render without changing the renderer's public signatures or CLI wiring. Preserve all renderer obligations. This is behavioral dormant construction within a module reached by core: production gates, Check and merge must never call the classifier yet. Keep the existing core_drift vocabulary unchanged; the later activation alone wires its gate and shared provider resolver.

The named tests exercise the entry's four states and refusal precedence, all marker corruption cases, and every modal and engine imperative the entry declares. Pin case-insensitive paragraph-opening subjects with word boundaries, Markdown unordered/numbered prefixes, whitespace collapse and multiline/list continuations. Include boundary near-misses and accepted other subjects, project-content directives, the dashboard example and process-like words later in a paragraph. Missing and drifted blocks direct repair through chupa core; process refusals direct rules to the engine template or project-content wording; marker repairs retain every project byte. Classification must not mutate its input or invoke filesystem, process, git, model or journal seams. Template-and-block changes from the candidate branch, rather than the running instance, determine currentness.

Pin the complete modal set: must, must not, should, should not, shall, shall not, will, will not, may, may not. Pin each process imperative: author, implement, check, review, merge, commit, dispatch, confirm, reject, kill, pause, resume, triage, rework, drain. Accept near-miss subjects such as chupacabra and directive tokens such as mustache or reviewer; refuse upper-case chupa directives and directives continued across physical lines, including numbered and unordered items. Only the project remainder is normalized for this predicate; the managed bytes retain their byte semantics.

## Scope fence
- chupa/hostfiles.py
- tests/test_hostfiles.py

## Acceptance criteria
1. `uv run pytest -q tests/test_hostfiles.py` exits 0 with test_classifier_entry_unit checking own and renderer required_units, unique resolve_plan_contract resolution, all entry_unit_gap parts and missing-part refusals.
2. `uv run pytest -q tests/test_hostfiles.py` exits 0 with test_core_drift_classification covering missing, current, drifted and refused for absent and marker-free inputs, matching and changed blocks, corruption/process-refusal precedence and input-byte identity. test_core_drift_refuses_marker_corruption covers every renderer corrupt-marker case and never classifies it green.
3. `uv run pytest -q tests/test_hostfiles.py` exits 0 with test_core_remainder_process_refusals covering all declared modals and imperatives, case, exact subject/word boundaries, both list-prefix forms and multiline normalization. test_core_remainder_accepts_project_rules covers other subjects, ordinary project requirements, The chupa dashboard must use dark mode., paragraph-opening near-misses and process-like text away from the opening.
4. `uv run pytest -q tests/test_hostfiles.py` exits 0 with test_core_drift_uses_branch_render proving a changed template with its new block is current while the old block is drifted; test_core_classifier_is_pure forbids write, process, git, model and journal effects while proving deterministic repeated classification.
5. `uv run pytest -q tests/test_hostfiles.py` exits 0 with test_core_classifier_unreachable_from_production_gates exercising actual production gate composition and merge rerun selection. It proves absence of classifier callers and active core_drift gate registration, while preserving the pre-existing vocabulary. The activation must fence and replace this negative assertion.
6. `uv run pytest -q tests/test_hostfiles.py tests/test_cli.py`, `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving renderer and CLI behavior, unchanged gates, Check and merge.

## Verification
```
uv run pytest -q tests/test_hostfiles.py
uv run pytest -q tests/test_hostfiles.py tests/test_cli.py
uv run pytest -q tests/test_gates.py tests/test_merge.py tests/test_stages.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
A missing governing fact returns premise_failed, kind: spec_gap naming its cited entry. A forced edit outside earned closure needs contract repair; no production activation or speculative API redesign.

## Time budget
- expected: 60m
- stuck: 90m
