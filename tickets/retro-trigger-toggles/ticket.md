---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/config.py
- chupa/retro.py::select_trigger
- chupa/retro.py::measurements
- tests/integration/test_retro.py::test_custom_trigger_settings_and_disabled_forcing
- tests/integration/test_retro.py::test_retro_trigger_boundaries
- tests/integration/test_config.py::test_retro_yaml_values
- tests/integration/test_host_contract.py::test_host_contract_schema_coverage
- tests/integration/test_host_contract.py::inventory
- docs/host-contract.md#Complete field inventory
- docs/how-chupa-works.md#9.5 Retro

## On-demand
- tests/integration/serve_rig.py

## Goal / Why
The automatic retro has one switch (`retro.enabled`) and three thresholds that are always armed: `every_merges`, `every_days`, and `spike_count`. An operator who wants only one trigger, for example retros every 7 days and never on merge count or spikes, cannot express it; setting a threshold very high only approximates it. The operator also cannot exclude a spike kind that is noisy for their host (2026-11-08).

After this change each trigger has its own `enabled` switch beside its threshold, the spike trigger takes an allowlist of the kinds that can fire it, and contradictory settings are refused at config load with the fix. `enabled` at the top of `retro:` stays the master switch for automatic retros; `chupa retro` still forces one.

## Scope in / Scope out
- In: `chupa/config.py`.
  - Add `SpikeKind = Literal["override", "rework", "gate-failure", "integration-red"]` next to the other `Literal` aliases.
  - Add `class RetroMerges(_Strict)`: `enabled: bool = True`, `every: Count = 25`.
  - Add `class RetroDays(_Strict)`: `enabled: bool = True`, `every: Count = 7`.
  - Add `class RetroSpikes(_Strict)`: `enabled: bool = True`, `count: Count = 5`, `kinds: list[SpikeKind]` with a default of every `SpikeKind` value in declaration order and `min_length=1`.
  - `class Retro(_Strict)` becomes `enabled: bool = True`, `merges: RetroMerges = RetroMerges()`, `days: RetroDays = RetroDays()`, `spikes: RetroSpikes = RetroSpikes()`. The flat keys `every_merges`, `every_days` and `spike_count` are removed in place; no alias reads them. An old config that still sets them is refused as an unknown key by the existing strict validation.
  - Config load refuses, as a `ConfigError` whose key is the dotted path:
    - `retro.enabled: true` while `merges.enabled`, `days.enabled` and `spikes.enabled` are all false. Key `retro.enabled`; the fix names `retro.enabled: false`.
    - A duplicate entry in `retro.spikes.kinds`. Key `retro.spikes.kinds`; the fix says to list each kind once.
  - `retro.enabled: false` with sub-triggers left enabled is valid: the master switch wins.
- In: `chupa/retro.py`.
  - `measurements` builds its `spikes` dict from `typing.get_args(SpikeKind)` instead of the literal tuple, so the config vocabulary and the counter cannot diverge.
  - `select_trigger` keeps its signature and return values. Unforced:
    - returns `None` when `settings.enabled` is false;
    - returns `"merges"` only when `merges.enabled` and the merge count reaches `merges.every`;
    - returns `"elapsed"` only when `days.enabled` and the window age reaches `days.every` days;
    - returns a spike kind only when `spikes.enabled`, that kind is in `spikes.kinds`, and its count reaches `spikes.count`.
  - The forced path is unchanged.
  - Measurements still report counts for every spike kind, including excluded ones; exclusion only stops a kind from firing the trigger.
- In: tests.
  - `tests/integration/test_retro.py::test_custom_trigger_settings_and_disabled_forcing` builds its settings with the nested shape.
  - New tests in `tests/integration/test_retro.py`:
    - `test_disabled_trigger_never_fires`: with `merges.enabled: false` and 25 merges, `select_trigger` returns `None`, not `"merges"`; likewise `days.enabled: false` past 7 days returns `None`, not `"elapsed"`; `spikes.enabled: false` with 5 rework spikes returns `None`, not `"rework"`.
    - `test_excluded_spike_kind_never_fires`: with `spikes.kinds: [override]` and 5 rework spikes, `select_trigger` returns `None`, not `"rework"`, and `measurements` still reports `rework: 5`.
  - `tests/integration/test_config.py`: the defaults assertion and `test_retro_yaml_values` use the nested shape. New tests: the all-triggers-off config and the duplicate-kind config each raise `ConfigError` with the keys above; a config with `every_merges` raises `ConfigError` (unknown key).
  - `tests/integration/serve_rig.py` writes `retro:` with the nested shape: `enabled` per mode and `merges: {every: 1}`.
  - `tests/integration/test_host_contract.py::test_host_contract_schema_coverage` also asserts that `config-values` row `spike_kind` equals `list(get_args(config.SpikeKind))`.
- In: docs.
  - `docs/host-contract.md` `config-fields`: the `Config.defaults.retro` object and the `Retro` row use the nested shape; add rows `RetroMerges`, `RetroDays` and `RetroSpikes`. `config-values` gains `spike_kind: [override, rework, gate-failure, integration-red]`.
  - `docs/how-chupa-works.md` section 9.5 describes the per-trigger switches, the `kinds` allowlist, the master switch and the two load refusals. Section 11's `retro` row names `enabled`, `merges`, `days` and `spikes`.
- Out: new spike kinds, test timing or coverage measurements, retro prompt or proposal changes, the VS Code extension.

## Scope fence
- chupa/config.py
- chupa/retro.py
- tests/integration/test_retro.py
- tests/integration/test_config.py
- tests/integration/test_host_contract.py
- tests/integration/serve_rig.py
- docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_retro.py tests/integration/test_config.py tests/integration/test_host_contract.py` exits 0, including `test_disabled_trigger_never_fires` and `test_excluded_spike_kind_never_fires`, which rule out a disabled trigger or excluded kind still firing.
2. In `tests/integration/test_config.py`, the all-triggers-off case asserts `ConfigError.key == "retro.enabled"`, not a silently accepted config that never fires.
3. With defaults, `select_trigger` returns the same values as before for every case in `tests/integration/test_retro.py::test_retro_trigger_boundaries`.
4. `docs/host-contract.md` and `docs/how-chupa-works.md` section 9.5 describe the nested `retro:` shape.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_retro.py tests/integration/test_config.py tests/integration/test_host_contract.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the defaults change which trigger fires for any input;
- a flat key (`every_merges`, `every_days`, `spike_count`) is still accepted, or an alias maps it;
- `retro.enabled: false` blocks a forced `retro`;
- an excluded spike kind is dropped from the reported measurements.

## Time budget
- expected: 45m
- stuck: 120m
