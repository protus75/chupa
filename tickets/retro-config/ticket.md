---
state: confirmed
source: human
priority: P3
kind: feature
---

## Depends on
none

## Context
- chupa/retro.py
- chupa/config.py
- tests/test_retro.py
- tests/test_config.py
- tests/test_host_contract.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Goal / Why
The automatic retro fires on fixed constants in `chupa/retro.py` `select_trigger`:
- 25 merges in the window;
- 7 days since the window started;
- 5 events of one spike kind.

It cannot be turned off. An operator who wants retros less often, more often, or only on demand has to edit code (2026-11-06). After this change, a `retro:` section in `config.yaml` sets these values, with defaults equal to today's behavior. `enabled: false` stops the automatic retro, and `chupa retro` still forces one.

## Scope in / Scope out
- In: `chupa/config.py`: `class Retro(_Strict)` with:
  - `enabled: bool = True`;
  - `every_merges: Count = 25`;
  - `every_days: Count = 7`;
  - `spike_count: Count = 5`.

  `Config` gets `retro: Retro = Retro()`, following the `Drain` section.
- In: `chupa/retro.py` `select_trigger` takes the `Retro` settings as an argument and uses them in place of 25, 7, and 5. When `enabled` is false and the retro is not forced, it returns `None`. The forced path is unchanged. The caller in the same file passes the checkout's `config.retro`.
- In: tests.
  - `tests/test_retro.py`: `select_trigger` honors custom `every_merges`, `every_days`, and `spike_count`, and returns `None` when `enabled` is false unless forced. With the defaults it returns exactly what it returns today.
  - `tests/test_config.py`: `retro` defaults and parses from YAML.
- In: docs.
  - `docs/host-contract.md`: add `Retro` and its fields to the `config-fields` inventory, which `tests/test_host_contract.py::test_host_contract_schema_coverage` checks.
  - `docs/how-chupa-works.md` section 9.5: the triggers come from `retro:`, `enabled: false` leaves only `retro`.
  - Section 11: the `retro:` keys.
- Out: the spike kinds, retro content, the `retro` verb, and the VS Code extension.

## Scope fence
- chupa/config.py
- chupa/retro.py
- tests/test_retro.py
- tests/test_config.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. `uv run pytest -q tests/test_retro.py tests/test_config.py tests/test_host_contract.py` exits 0, including the tests above.
2. `docs/how-chupa-works.md` sections 9.5 and 11 and `docs/host-contract.md` describe `retro:`.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_retro.py tests/test_config.py tests/test_host_contract.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- the defaults change today's trigger behavior;
- `enabled: false` blocks a forced `retro`;
- a threshold stays hard-coded.

## Time budget
- expected: 30m
- stuck: 90m
