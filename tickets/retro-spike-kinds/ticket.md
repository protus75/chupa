---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- retro-trigger-toggles

## Context
- chupa/config.py
- chupa/retro.py::measurements
- chupa/retro.py::select_trigger
- chupa/status.py::reject_queue
- chupa/runner.py::failure_terminal
- chupa/flake.py
- chupa/box.py::RereportJournal
- tests/integration/test_retro.py::test_retro_trigger_boundaries
- tests/integration/test_retro.py::test_mixed_spikes_do_not_sum_and_new_invocations_do_count
- docs/how-chupa-works.md#9.5 Retro

## On-demand
- tests/integration/test_scorecard.py
- tests/integration/test_status.py
- tests/integration/test_config.py
- docs/host-contract.md

## Goal / Why
The spike trigger counts four kinds: `override`, `rework`, `gate-failure` and `integration-red`. Other repeated failures already journaled never fire a retro: tickets routed to the Reject queue, premise failures, infrastructure errors, flaky tests, and tombstoned problems that came back (2026-11-08). After this change five more spike kinds are counted from existing journal events, reported in the retro measurements, shown in the scorecard signal counts, and selectable in `retro.spikes.kinds`. No new journal emitter is added.

## Scope in / Scope out
- In: `chupa/config.py` `SpikeKind` gains `"reject"`, `"premise-failed"`, `"infra-error"`, `"flake"` and `"escape"`, after the existing four. The `retro.spikes.kinds` default stays every `SpikeKind` value, so all nine kinds are included by default.
- In: `chupa/retro.py` `measurements` counts each new kind once per identity. The run identity is the existing `(stem, run sequence)` pair already used for `gate-failure`.
  - `reject`: a `state_transition` whose body has `routed: reject_queue`, or a `reject_arrival` signal for the stem; both for one run count once.
  - `premise-failed`: a `state_transition` to `premise_failed`.
  - `infra-error`: a `state_transition` to `infra_error`, including `reason: provider_drought`.
  - `flake`: a signal with `kind: flake_detected`; its identity is the event key `flake/<box_id>`.
  - `escape`: a signal with `kind: tombstone_auto_reopened`; its identity is the event key `tombstone-reopen/<box_id>/<reports>`.
  - A duplicated event with the same identity never counts twice, as for the existing kinds.
- In: tests.
  - `tests/integration/test_retro.py::test_retro_trigger_boundaries` parametrizes all nine kinds. Each new kind appends its journal events directly and fires at exactly `count`, not at `count - 1`; a duplicated record does not advance the count.
  - `tests/integration/test_retro.py::test_mixed_spikes_do_not_sum_and_new_invocations_do_count` and the signal-count assertions in `tests/integration/test_scorecard.py` and `tests/integration/test_status.py` expect the five new keys at 0.
  - `tests/integration/test_config.py`: the `retro` defaults assertion lists all nine kinds.
- In: docs. `docs/host-contract.md` `config-values` `spike_kind` and the `RetroSpikes` `kinds` default list all nine kinds. `docs/how-chupa-works.md` section 9.5 names each kind and the event it counts.
- Out: trigger switches, per-kind thresholds, timeout or storm-breaker kinds, test timing and coverage, and the retro prompt.

## Scope fence
- chupa/config.py
- chupa/retro.py
- tests/integration/test_retro.py
- tests/integration/test_scorecard.py
- tests/integration/test_status.py
- tests/integration/test_config.py
- tests/integration/test_host_contract.py
- docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_retro.py` exits 0. `test_retro_trigger_boundaries[reject]`, `[premise-failed]`, `[infra-error]`, `[flake]` and `[escape]` each fail if the kind is not counted, or if a duplicated record is counted twice.
2. `./dev.py test tests/integration/test_scorecard.py tests/integration/test_status.py tests/integration/test_config.py tests/integration/test_host_contract.py` exits 0.
3. `docs/how-chupa-works.md` section 9.5 lists all nine spike kinds.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_retro.py
./dev.py test tests/integration/test_scorecard.py tests/integration/test_status.py tests/integration/test_config.py tests/integration/test_host_contract.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a new journal signal or emitter is added to produce a spike;
- a `reject_arrival` and its routed terminal for one run count as two rejects;
- an existing kind's count changes for the same journal.

## Time budget
- expected: 40m
- stuck: 120m
