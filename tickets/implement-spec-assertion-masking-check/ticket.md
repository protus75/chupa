---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: draft
---
## Depends on

- none

## Context

- tests/unit/test_specs.py
- tests/integration/test_stages.py

## On-demand

- chupa/specs/implement.md
- docs/how-chupa-works.md

## Goal / Why

The assertion rule in `chupa/specs/implement.md` (the paragraph beginning "For each assertion, name the likely wrong implementation it rules out") has Implement only claim that an assertion is discriminating. It never has Implement show it. When another fixture rule hides the targeted filter, the claim is false and only Review catches it. Fungo retro window 22 recorded 3 review rejections from this pattern (s11-rates-faced twice, s11-rates-counts once), which cost retries and one tier escalation. Fungo's host-local `docs/TESTING.md` substitute was rejected (see `host-process-stays-upstream`), so the repair belongs in this spec, where every host gets it.

After this change the paragraph adds a check for filter, exclusion, ordering and tie-break assertions. The target row must pass every other filter, and its derived columns must give the intended role. Implement applies the wrong version once in the worktree, confirms the test fails, then restores the code. The description of the rule in `docs/how-chupa-works.md` is updated in the same change, since documentation follows changes.

The class is prevented by the unit test that pins the new sentences. Later retro windows should show no review rejection whose finding says another fixture rule masked a filter, exclusion or tie-break assertion.

## Scope in / Scope out

Scope in:

- Add one sentence group to the assertion paragraph of the Task section in `chupa/specs/implement.md`. For an assertion on a filter, exclusion, ordering or tie-break, the target row must pass every other filter and its derived columns must give the intended role. Implement then applies the wrong version once in the worktree, confirms the test fails, and restores it before committing.
- Bump the spec `version` to the next minor above the version on main.
- Update the version pins in `tests/unit/test_specs.py` and `tests/integration/test_stages.py` to the bumped version, and pin the new sentences in `tests/unit/test_specs.py`.
- Update the paragraph at `docs/how-chupa-works.md` lines 228-231, which lists the parts of the Implement assertion rule, so it also states the new check: the target row passes every other filter, its derived columns give the intended role, and the wrong version is applied once to confirm the test fails.

Scope out: edit-weakening and matcher-literal rules (declined records 000313 and 000393), mapping criteria to tests (`implement-spec-criteria-to-tests`), and the host authoring path (`host-process-stays-upstream`).

## Scope fence

- chupa/specs/implement.md
- docs/how-chupa-works.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py

## Acceptance criteria

- The assertion paragraph in `chupa/specs/implement.md` states that the target row must pass every other filter and that its derived columns must give the intended role, pinned by `./dev.py test tests/unit/test_specs.py`. A spec without this sentence fails that pin.
- The paragraph tells Implement to apply the wrong version once in the worktree, confirm the test fails, then restore it. The pin in `./dev.py test tests/unit/test_specs.py` fails on a spec that only claims the assertion is discriminating.
- The `version` in `chupa/specs/implement.md` is the next minor above the version on main. Both `./dev.py test tests/unit/test_specs.py` and `./dev.py test tests/integration/test_stages.py` pin it, and each fails if the file keeps the old version.
- The existing assertion-rule pins still pass in `./dev.py test tests/unit/test_specs.py`.
- The assertion-rule paragraph in `docs/how-chupa-works.md` (formerly lines 228-231) states the new check for filter, exclusion, ordering and tie-break assertions: the target row passes every other filter, its derived columns give the intended role, and the wrong version is applied once to confirm the test fails.

## Verification

```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
```

## Definition of rejected

Rejected if the sentence is added to another spec or to a host's own files (a host repository's `docs/TESTING.md` or similar), if `docs/how-chupa-works.md` still describes the old rule, if the version is not the next minor above main, if a pin for the new text or version is missing, or if the diff changes any file outside the fence.

## Time budget

- expected: 15m
- stuck: 45m
