---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/author.py::author
- chupa/author.py::failure_declined
- chupa/hostfiles.py::CORE_TEMPLATE
- tests/integration/test_author.py::test_reopened_retro_ticket_starts_draft
- tests/integration/test_hostfiles.py::test_core_template_is_host_neutral
- docs/how-chupa-works.md#9.3 Author and starting state

## Goal / Why
A host's pipeline can turn a repair that belongs in chupa into a host ticket that copies or patches chupa's rule in host files. On 2026-11-11 the fungo host's retro 22 (`tickets/retro/000022.md` in fungo) proposed `"proposed_spec_paths": ["specs/implement.md"]`, a repair to chupa's implement spec. `author()` in `chupa/author.py` passes these to the Author model as `chupa/specs/implement.md`. Fungo does not track that file, because the chupa install owns it. The model wrote `testing-assertions-filter-tiebreak-clause` instead: a fungo ticket that pastes a restated implement rule into fungo's `docs/TESTING.md`. The owner rejected it. A host copy of a chupa rule competes with chupa's version, reaches no other host, and goes stale on upgrade. Repositories do not cross-talk, so the fix is not to file into chupa from a host. It is to stop the host from authoring a substitute, and to leave a record the owner can carry upstream by hand.

When this ticket is done:
- A `retro_finding` with any proposed spec path that the repository does not track is declined before any Author model call. Its decision record in `tickets/decisions/` names each untracked path and the retro report key, so the owner can carry the proposal to chupa. No host ticket is authored. In this repo, chupa tracks its own specs, so its retro spec proposals are authored as before.
- Every host's managed conduct block carries a rule that tells sessions and ticket agents not to copy or patch chupa process into host files.

Rule home: the new rule applies to every host, so its home is `CORE_TEMPLATE` in `chupa/hostfiles.py`. It reaches this repo's `CLAUDE.md` and `AGENTS.md` through `./dev.py core`. Nothing is added outside the managed blocks.

## Scope in / Scope out
Scope in:
- `chupa/author.py`, `author()`: move the tracked-files listing (`checkout.git.ls_files`) above the Author spec load. Directly after it, decline when the message's `proposed_spec_paths` contains any path whose repo form `chupa/<path>` is not a tracked file. The guard runs before `author()` reads the Author spec, any report, or calls the model, so a unit test reaches it with a fake checkout. Decline through the existing `failure_declined`. Its evidence string names every untracked `chupa/<path>`, includes the message's `retro_report_key`, and states that the chupa install owns these specs, so the owner carries the proposal to chupa. A message with no proposed spec paths, or one whose proposed spec paths are all tracked, proceeds unchanged.
- `tests/unit/test_author.py`: add a parametrized test that calls `author()` on a `retro_finding` message with an `author` verdict. It uses a fake checkout whose `git.ls_files` returns a fixed list, and monkeypatches `failure_declined` to record its evidence and return a sentinel. Case 1: `proposed_spec_paths=["specs/implement.md"]`, with a tracked list that has no `chupa/specs/` file. Case 2: `["specs/review.md", "specs/implement.md"]`, with `chupa/specs/review.md` tracked. For both cases, assert that `author()` returns the sentinel, and that the evidence contains `chupa/specs/implement.md` and the message's retro report key. Case 2 also asserts that the evidence does not contain `chupa/specs/review.md`.
- `tests/unit/test_hostfiles.py` is fenced because `chupa/hostfiles.py` has a unit coverage floor. Edit it only if the template change breaks it.
- `tests/integration/test_author.py`: the existing tests `test_author_uses_baseline_resolution` (its `retro_finding` row), `test_reopened_retro_ticket_starts_draft`, and `test_retro_author_bridge_and_resolution_recover_without_another_call` must commit a fixture file at `chupa/<path>` for each of their proposed spec paths before they run, so they keep exercising the authored path. Their assertions are unchanged.
- `chupa/hostfiles.py`, `CORE_TEMPLATE`: append this bullet, verbatim, as the last bullet of `## Diagnosis`:
  `- HARD: A fix that belongs in chupa (a prompt spec, gate, ticket format, host guide, or this block) is never copied or patched into host files. Report it for the owner to carry to chupa, then stop. Why: a host copy competes with chupa's rule, reaches no other host, and goes stale on upgrade.`
- Run `./dev.py core` to refresh the managed blocks in `CLAUDE.md` and `AGENTS.md`. `core` does not route `hosts/fixture/CLAUDE.md`, so rewrite that file to `hostfiles.render` of its current bytes.
- `tests/integration/test_hostfiles.py`: regenerate `GOLDEN` with the module's `__main__` block. In `test_core_template_is_host_neutral`, add one pinned phrase: `is never copied or patched into host files`.
- `docs/how-chupa-works.md`, section `9.3 Author and starting state`: add one sentence. It says that a `retro_finding` naming a spec path the repository does not track is declined before the Author call, with a decision record that names the paths and the retro report for the owner to carry to chupa.

Scope out:
- `chupa/specs/retro.md`, `chupa/specs/triage.md`, `chupa/specs/author.md`, and every other prompt spec. The retro still proposes spec repairs in a host, because the proposal is the evidence the owner carries upstream.
- Any write to a repository other than the one being triaged, and any channel from a host to chupa's Suggestion Box.
- `suggestion` and other message classes, and the `test_issue` / `proposed_paths` proposal form.
- Text outside the `chupa:core` markers in `CLAUDE.md`, `AGENTS.md`, and `hosts/fixture/CLAUDE.md`. Every other `CORE_TEMPLATE` bullet.

## Scope fence
- chupa/author.py
- chupa/hostfiles.py
- CLAUDE.md
- AGENTS.md
- hosts/fixture/CLAUDE.md
- docs/how-chupa-works.md
- tests/integration/test_author.py
- tests/integration/test_hostfiles.py
- tests/unit/test_author.py
- tests/unit/test_hostfiles.py

## Acceptance criteria
1. `./dev.py test tests/unit/test_author.py` passes, including the new parametrized decline test. If the guard is missing, `author()` goes on to the spec load instead of returning the sentinel, which fails case 1. If the guard declines only when no proposed path is tracked, case 2 never declines and fails. If the evidence omits the untracked path or the retro report key, both cases fail.
2. `./dev.py test tests/integration/test_author.py` passes. `test_author_uses_baseline_resolution`, `test_reopened_retro_ticket_starts_draft`, and `test_retro_author_bridge_and_resolution_recover_without_another_call` still author their tickets, with their fixture spec files tracked. A guard that declines every spec proposal fails them.
3. `./dev.py test tests/integration/test_hostfiles.py` passes. `test_core_template_is_host_neutral` fails if `CORE_TEMPLATE` lacks `is never copied or patched into host files`, and the size test fails if the template exceeds 8192 bytes.
4. `./dev.py test tests/integration/test_fixture_host.py` passes, and the `core_drift` gate passes. `classify_core` reports `current` for `CLAUDE.md`, `AGENTS.md`, and `hosts/fixture/CLAUDE.md`, so a hand-edited or stale managed block fails.
5. `docs/how-chupa-works.md` section `9.3 Author and starting state` states the untracked-spec decline.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/unit/test_author.py tests/unit/test_hostfiles.py tests/integration/test_author.py tests/integration/test_hostfiles.py tests/integration/test_fixture_host.py
./dev.py test
```

## Definition of rejected
- A retro spec proposal whose paths are all tracked is declined, or any message class other than `retro_finding` is affected.
- The change writes to, or files into, any repository other than the one being triaged.
- Any prompt spec changes, or the retro stops proposing spec paths in a host.
- The new `CORE_TEMPLATE` bullet differs from the Scope in text or sits outside `## Diagnosis`, or another template bullet changes.
- `CLAUDE.md`, `AGENTS.md`, or `hosts/fixture/CLAUDE.md` changes outside its `chupa:core` markers.

## Time budget
- expected: 35m
- stuck: 80m
