---
priority: P1
kind: bug
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on

- none

## Context

- chupa/drain.py::record_reoffer
- chupa/runner.py
- tests/integration/test_drain.py::test_reoffer_rules_and_recording
- docs/how-chupa-works.md

## Goal / Why

`record_reoffer` draws a `retry` cap unit for every terminal except `premise_failed` and provider-drought ones. `chupa/runner.py` already draws `infra` when an `infra_error` or `timeout` terminal is reached. Each such failure therefore costs two cap units: one `infra`, then one `retry` at the re-offer. The stem can park under the wrong cap, with the wrong reason and paved road. Infra failures are common (e.g. read-only Review ending `infra_error`), and they spend the retry budget that gate failures need. The premise lane already got this split: `premise_failed` re-offers skip the retry draw because the runner draws `premise_bounce`. After this change an `infra_error` or `timeout` re-offer draws no `retry` unit, in drain and in serve (both call `record_reoffer`).

## Scope in / Scope out

In: `record_reoffer` skips the `retry` draw when the last terminal is `infra_error` or `timeout`. A new unit test file `tests/unit/test_drain_reoffer.py` calls `record_reoffer` with a fake journal (an object whose `append` records its calls) and in-memory `Event` histories, one per terminal, and asserts which `cap_consumed` events each terminal class produces; no disk or process access. `docs/how-chupa-works.md` is updated where it describes the retry draw exclusions.

Out: `abandoned` reaps. The runner draws no `infra` unit for them, so skipping the retry draw would leave them undrawn. Changes to `runner.py` or caps config. Changes to the machine keep signal.

- In: a carried reproducer `tests/regress_reoffer_infra_retry.py`, shaped like `tests/regress_dev_test_args.py`. It runs `pytest.main(["tests/unit/test_drain_reoffer.py", "-k", "infra_error", "-q", "-p", "no:cacheprovider"])` in-process with stdout redirected to stderr, then prints exactly one JSON object: `{"regression_result": "pass"}` with exit 0 when pytest returns 0, `{"regression_result": "defect"}` with exit 1 when pytest returns 1 (the test failed), and `{"regression_result": "error"}` with exit 2 otherwise (including no test collected) or on any exception. It uses only code present at the base commit; on the base overlaid with the carried files the named test fails, so it prints `defect`.

## Scope fence

- chupa/drain.py
- tests/integration/test_drain.py
- tests/unit/test_drain_reoffer.py
- tests/regress_reoffer_infra_retry.py
- docs/how-chupa-works.md

## Acceptance criteria

- `record_reoffer` on an `infra_error` terminal appends no `retry` `cap_consumed`, checked by `./dev.py test tests/unit/test_drain_reoffer.py`. The test fails if a `retry` draw is still appended.
- `record_reoffer` on a `timeout` terminal appends no `retry` draw, checked by `./dev.py test tests/unit/test_drain_reoffer.py`. The test fails if a `retry` draw is still appended.
- `record_reoffer` on a `gate_failed` terminal still appends the `retry` draw, checked by `./dev.py test tests/unit/test_drain_reoffer.py`. The test fails if the draw is dropped for it.
- `record_reoffer` on an `abandoned` terminal still appends the `retry` `cap_consumed`, checked by `./dev.py test tests/unit/test_drain_reoffer.py`. The test fails if the draw is dropped for it.
- `./dev.py test tests/integration/test_drain.py -k reoffer` exits 0.
- `docs/how-chupa-works.md` names `infra_error` and `timeout` among the terminals that draw no `retry` on re-offer; check with `tests/integration/test_drain.py` and a review of that doc line.
- `uv run python tests/regress_reoffer_infra_retry.py` prints only `{"regression_result": "pass"}` and exits 0 on the fixed code, and prints only `{"regression_result": "defect"}` with a nonzero exit on the unfixed code, which rules out a reproducer whose stdout carries pytest output or whose verdict ignores the test result.

## Verification

```
./dev.py test tests/unit/test_drain_reoffer.py
./dev.py test tests/integration/test_drain.py -k reoffer
```

## Regression

```
uv run python tests/regress_reoffer_infra_retry.py
```

- carries: tests/unit/test_drain_reoffer.py
- carries: tests/regress_reoffer_infra_retry.py

## Definition of rejected

Rejected if `abandoned` reaps lose their retry draw, if `runner.py` is touched, or if the new test also passes while `record_reoffer` still draws `retry` for `infra_error`.

## Time budget

- expected: 20m
- stuck: 60m
