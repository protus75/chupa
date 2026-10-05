---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- requisition-seed-path

## Context
- chupa/journal.py
- chupa/artifacts.py

## Plan contract
- 19.L
- 19.P2
- section 6
- section 15

## Goal / Why
`chupa/audit.py` is the invariant auditor (section 15 harness ladder rung 1): a closed set of named invariants folded over a journal, each a pure check over `Journal.read_segments()`, returning every violation with the invariant's name. A green journal yields no violation.

Why: the shakeout battery's pass condition is this auditor (19.P2): a member is green only when its terminal is right AND its own journal folds clean. Without it, a battery can pass a run that journaled two terminals, drew an undeclared cap, or merged with an unpaired effect intent.

Owners (19.P2 NAMES): `chupa/audit.py` / `tests/test_audit.py` own the invariant set and the fold. `chupa/journal.py` owns the one parser (`read_segments`) and the run-state vocabulary (`TERMINAL_STATES`), read only. `chupa/caps.py` owns the declared cap vocabulary (`CAPS`), read only.

## Scope in / Scope out
- In: `chupa/audit.py`:
  - `INVARIANTS`, the closed ordered tuple `("one_terminal_per_run", "declared_cap", "merged_effects_paired", "merged_carries_commit", "closed_run_states", "segment_ts_monotonic")`.
  - `Violation`, a frozen dataclass: `invariant`, `ticket` (nullable), `detail`.
  - `audit(segments: Iterable[tuple[Event, ...]], caps: Collection[str] = CAPS) -> list[Violation]`, in segment then event order:
    - `one_terminal_per_run`: per stem, a run opens at each `state_transition` `to: running` and closes at the next one. A run journaling more than one terminal is a violation. A terminal outside any run is a violation unless it is `rejected` (the `reject` verb's journal-only kill). A run with NO terminal is reconcile's orphan, never a violation.
    - `declared_cap`: every `cap_consumed` body names a cap in `caps`.
    - `merged_effects_paired`: in a run that reached `merged`, every `effect_intent` on that stem has an `effect_completion` with the same key. Every non-ok terminal is exempt (closed-run history, section 11.2), and so is a run with no terminal.
    - `merged_carries_commit`: every `to: merged` body carries the key `commit`, a 40-hex string or null (null only for a settlement that admitted no code).
    - `closed_run_states`: every `state_transition` `to` is `running` or in `TERMINAL_STATES`.
    - `segment_ts_monotonic`: within each segment, `ts` never decreases (string order, the pinned rendering, section 6).
  - `audit_journal(journal: Journal, caps=CAPS) -> list[Violation]` folds `journal.read_segments()`.
- Out: running it continuously against a live daemon (Phase 3), any CLI verb, any change to `chupa/journal.py` or `chupa/caps.py`, and the battery members (later seeds).

## Scope fence
- chupa/audit.py
- tests/test_audit.py

## Acceptance criteria
1. `tests/test_audit.py` proves a journal produced by a production `drain` over a temp checkout with a FakeLLM, one ticket merged and one parked red, yields `audit_journal(...) == []`.
2. `tests/test_audit.py` plants one violation per invariant into an otherwise-green journal and proves `audit` returns exactly one violation naming that invariant, for each of the six names in `INVARIANTS`.
3. `tests/test_audit.py` proves the exemptions: an unpaired intent in a `gate_failed` run, an orphan `running` with no terminal, a journal-only `rejected` after a terminal, and `to: merged` with `commit: null` each yield no violation.
4. `tests/test_audit.py` proves `segment_ts_monotonic` is per segment: two segments whose second starts earlier than the first ends, each internally ordered, yield no violation.
5. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_audit.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- An invariant reads the journal through anything but `read_segments`, or a violation is skipped silently.
- An invariant outside the closed six exists, or a non-ok run is held to effect pairing.
- The diff touches a file outside the fence.

## Time budget
- expected: 45m
- stuck: 90m
