---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- escalation-ladder
- suggestion-box

## Context
- chupa/config.py
- tests/test_eval_harness.py
- eval/harness.py

## Plan contract
- 19.L
- 19.P2
- section 12

## Goal / Why
`chupa/policy.py` resolves the starting state of a box-authored ticket from section 12's policy table (`config.box_policy`) plus the scope override, in EVERY era, with no drain special case:
- A reopen, an absent or revoked or identity-drifted GO baseline, an undeclared safety inventory, a fence touching the inventory, or a non-empty `gate_bypass` each resolve `draft`.
- Only a standing GO with nothing else firing resolves the table row.

The bootstrap self-build never records GO, so every box-authored ticket starts `draft`, and the operator who ran `chupa triage` confirms the few worth building. `tests/test_policy.py` pins that protected instance.

Why: the Author stage (the next seed batch) writes the tickets triage asks for and must stamp each one's starting state before its paid call (19.P2 BOX). Without one owner, the GO read, the inventory override, and the table would be re-derived at each authoring site. There is NO self-build auto-confirm exemption: a human is present at every bootstrap scan, and nothing from the box runs unattended (section 12). The daemon-era continuous consumer is a separate era built with the daemon, never here.

Owners (19.P2 NAMES): `chupa/policy.py` / `tests/test_policy.py` own the starting-state resolution and the GO-baseline read. The baseline identity it compares moves here from `eval/harness.py`, renamed in place, and the harness imports it. `chupa/config.py` already parses `box_policy` (absent rows take the table defaults) and `engine_plane_safety_inventory`, and is read only. `chupa/box.py` (from `suggestion-box`) owns the message class vocabulary.

## Scope in / Scope out
- In: `chupa/policy.py`:
  - `BASELINE_SIGNAL = "review_baseline"`, `BASELINED_SURFACES = ("review", "author")`, `TIERS`, and `baseline_identity(config, specs_dir)` MOVE here from `eval/harness.py` unchanged in behavior. `eval/harness.py` imports them and drops its own definitions. Its `SIGNAL` constant is renamed to `BASELINE_SIGNAL` at every use, with no alias left behind.
  - `go_binds(events, identity) -> bool`: True exactly when the LATEST `signal` whose body names `BASELINE_SIGNAL` has `verdict == "GO"` and an `identity` equal to `identity`. No signal is False. A later `NO_GO` revokes, and an identity mismatch (drift) is False.
  - `policy_row(message_class, bug_origin, has_repro) -> BoxRow` maps a message to its table row. `bug_report` maps to `bug_report_self_diagnosed` (`self_diagnosed`), `bug_report_player_repro` (`player` with a repro), or `bug_report_player_no_repro` (`player` without one). Every other class maps to the row of the same name. An unknown class or a `bug_report` missing either field raises `ValueError`.
  - `touches_inventory(fence, inventory) -> bool`: some fence prefix and some inventory prefix are equal, or one is a path-prefix of the other at a `/` boundary.
  - `start_state(config, *, row, fence, gate_bypass, go, reopen=False) -> StartState`, which resolves `draft` when ANY of these holds, else `config.box_policy[row]`:
    - `reopen` is set.
    - `go` is False.
    - `config.engine_plane_safety_inventory` is empty (undeclared fails closed).
    - The fence touches the inventory.
    - `gate_bypass` is non-empty.
- Out: any caller. The Author stage is the first consumer (the next seed batch). The daemon-era auto-confirm consumer, the supervised-merge hold, and the GO recording mode are later phases.
- Out: any change to `chupa/config.py`, `config.yaml`, `BOX_POLICY_DEFAULTS`, or what the review-baseline harness scores or journals.

## Scope fence
- chupa/policy.py
- tests/test_policy.py
- eval/harness.py

## Acceptance criteria
1. The `python -c` command in `## Verification` exits 0: `eval.harness.baseline_identity` is `chupa.policy.baseline_identity`, and `eval.harness` defines no `SIGNAL`.
2. `tests/test_policy.py` pins the bootstrap instance. With no baseline signal, and again with only the Phase 1 `NO_GO` signal, `start_state` resolves `draft` for EVERY row in `BOX_POLICY_DEFAULTS` (`failure_report` included), under a declared inventory and a fence outside it.
3. `tests/test_policy.py` proves a standing GO whose identity equals `baseline_identity(config)` resolves each row to its table value, and that each of these alone forces `draft`: a later `NO_GO`, a drifted identity, an empty inventory, a fence entry `specs/` against inventory `specs/triage.md` (and the reverse), a non-empty `gate_bypass`, and `reopen`. A fence `chupa/gatesx.py` does not touch inventory `chupa/gates.py`.
4. `tests/test_policy.py` proves `policy_row` maps all five classes and the three `bug_report` variants, and refuses an unknown class.
5. `uv run pytest -q tests/test_eval_harness.py` passes with no edit to that file.
6. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -c "import chupa.policy as p, eval.harness as h; assert h.baseline_identity is p.baseline_identity and not hasattr(h, 'SIGNAL')"
uv run pytest -q tests/test_policy.py tests/test_eval_harness.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- Any path resolves `confirmed` without a standing, identity-matched GO.
- A drain, era, or self-build special case appears.
- A second baseline-identity or GO read survives outside `chupa/policy.py`.
- The diff touches a file outside the fence.

## Time budget
- expected: 40m
- stuck: 80m
