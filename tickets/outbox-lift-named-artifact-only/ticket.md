---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on
- none

## Context
- chupa/stages.py::_lift_files
- chupa/stages.py::lift_outbox
- chupa/stages.py::_validate_reports
- chupa/stages.py::ArtifactInvalid
- tests/integration/test_stages.py
- docs/how-chupa-works.md#3.3 What the engine writes back

## Goal / Why
`lift_outbox` commits files from the agent-writable worktree outbox straight to `main`, with no scope fence or Review between the agent and that commit. `_lift_files` filters only by `only`, `ticket.md`, the KNOWN_ARTIFACTS name check and byte-equality with the canonical copy. The `run-record` lift (after Implement) and the `review` lift pass `only=None`, so every other file under the worktree's `tickets/<stem>/` is lifted. `p.is_file()` and `src.read_bytes()` follow symlinks, so a symlink to a file outside the worktree (for example one holding a provider key) is lifted with its target's content. Nothing bounds a lifted file's size.

After this change each lift commits only the artifact the engine names for it, never a symlink, and never a file over 256 KB. Every artifact lifted so far is `.md` or `.json` and at most 26 KB (largest `harvest.json`), so 256 KB is about 10x headroom. The named-file rule already fixes the extension, so no separate extension check is added.

Simplest approach: one pure predicate in `chupa/stages.py` decides each outbox path, so no caller changes and the rule is unit-testable without disk. Rejected: scrubbing lifted bytes through the Redactor (a new writer site and more scope than the stray-file and symlink paths need), and threading a new `only=` argument through every caller (leaves direct `lift_outbox` callers in tests unprotected).

## Scope in / Scope out
In:
- A pure predicate in `chupa/stages.py`, `_lift_decision(kind: str, only: str | None, rel: str, is_symlink: bool, size: int) -> Literal["skip", "lift", "too_large"]`, plus a constant `LIFT_MAX_BYTES = 256 * 1024`. Rules, in order:
  - a symlink is `skip`;
  - when `only` is given, only `rel == only` is selected, for any kind (this covers `diagnosis`, `harvest` and `harvest-rework`);
  - when `only` is None, `run-record` selects only `run.md`, `review` selects only `review.md`, and `checks` selects only `checks.json` plus registered KNOWN_ARTIFACTS names;
  - a selected path with `size > LIFT_MAX_BYTES` is `too_large`, otherwise `lift`; anything not selected is `skip`.
- `_lift_files` keeps its existing `ticket.md` and byte-equality exclusions, calls `_lift_decision` with `p.is_symlink()` and `p.lstat().st_size`, and only examines entries for which `p.is_symlink() or p.is_file()`. A `too_large` path raises `ArtifactInvalid(path, ValueError(f"artifact is {size} bytes, over the {LIFT_MAX_BYTES}-byte lift limit"))`, the same failure a malformed registered report already produces.
- Tests:
  - new unit test file `tests/unit/test_lift_decision.py` (pure, no disk): `test_lift_decision_selects_named_artifact_per_kind` (a `review` lift skips `run.md` and `notes.txt`; `checks` lifts `checks.json` and a KNOWN_ARTIFACTS name), `test_lift_decision_skips_symlink` (a symlinked `run.md` is `skip`), `test_lift_decision_only_overrides_kind` (`kind="harvest-rework"` with `only` set lifts that path), and `test_lift_decision_size_limit` (`LIFT_MAX_BYTES` is `lift`, `LIFT_MAX_BYTES + 1` is `too_large`).
  - integration tests in `tests/integration/test_stages.py`, all matching `-k outbox_lift`, for the stray-file, symlink and oversize behaviours in Acceptance criteria 1-3.
- `docs/how-chupa-works.md` section 3.3: one sentence saying each lift takes only its named artifact, refuses symlinks, and refuses a file over 256 KB.
- The other coverage-dependent test files that run `chupa/stages.py` (for example `tests/integration/test_merge.py`, `test_daemon_soak.py`, `test_reliability_battery.py`, `test_harvest.py`, `test_diagnose.py`) are unaffected. Direct `lift_outbox` callers lift registered reports under `checks` (still selected) or expect `None` from `run-record`/`review` lifts of unnamed or byte-equal files (still skipped). Harvest and diagnosis pass `only`, which still selects exactly that path. No fixture uses a symlink or a file near 256 KB, so every other dependent sees the same lifted file set.

Out:
- Redacting lifted bytes, and any change to `chupa/redact.py`.
- Gate and fence changes; journal scrubbing.
- Read-only tool restriction, which is covered by `claude-readonly-hard-tool-restriction`.
- Any change to the `lift_outbox` signature or its callers.

## Scope fence
- chupa/stages.py
- tests/integration/test_stages.py
- tests/unit/test_lift_decision.py
- docs/how-chupa-works.md

## Acceptance criteria
1. With an extra file `notes.txt` in the outbox, the `run-record` lift commits only `run.md`. The test asserts `notes.txt` is absent from the commit and from `tickets/<stem>/` on `main`; a test that also passes when `notes.txt` is committed checks nothing. Checked by `./dev.py test tests/integration/test_stages.py -k outbox_lift`.
2. A symlinked `run.md` pointing at a file outside the worktree holding a secret is not committed. The test asserts the target's content appears nowhere on `main`. Checked by `./dev.py test tests/integration/test_stages.py -k outbox_lift`.
3. A `run.md` of `LIFT_MAX_BYTES + 1` bytes makes the `run-record` lift raise `ArtifactInvalid` naming the size and limit, and nothing is committed. Checked by `./dev.py test tests/integration/test_stages.py -k outbox_lift`.
4. `./dev.py test tests/unit/test_lift_decision.py` exits 0 with the four named tests. The per-kind test rules out a `review` lift that still selects `run.md`; the `only` test rules out a closed kind table that drops `harvest-rework`; the size test pins the boundary on both sides.
5. The existing `checks` and `review` lift tests still pass: `./dev.py test tests/integration` exits 0.
6. `docs/how-chupa-works.md` section 3.3 states the lift "refuses symlinks". Checked by `grep -n "refuses symlinks" docs/how-chupa-works.md`, a phrase only the new sentence contains.

## Verification
```
./dev.py test tests/integration/test_stages.py -k outbox_lift
./dev.py test tests/unit/test_lift_decision.py
./dev.py test tests/integration
grep -n "refuses symlinks" docs/how-chupa-works.md
```

## Definition of rejected
A lift kind still commits an unnamed file, a symlink or its target, or a file over 256 KB; or a `harvest-rework` lift with `only` set commits nothing; or the fix adds a gate, config knob, redaction, or a `lift_outbox` signature change.

## Time budget
- expected: 40m
- stuck: 80m
