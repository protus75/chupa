---
priority: P1
kind: bug
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: draft
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

In: `record_reoffer` skips the `retry` draw when the last terminal is `infra_error` or `timeout`. A drain test covers which `cap_consumed` events each terminal class produces. `docs/how-chupa-works.md` is updated where it describes the retry draw exclusions.

Out: `abandoned` reaps. The runner draws no `infra` unit for them, so skipping the retry draw would leave them undrawn. Changes to `runner.py` or caps config. Changes to the machine keep signal.

## Scope fence

- chupa/drain.py
- tests/integration/test_drain.py
- docs/how-chupa-works.md

## Acceptance criteria

- `record_reoffer` on an `infra_error` terminal appends only the machine keep and no `retry` `cap_consumed`, checked by `./dev.py test tests/integration/test_drain.py -k reoffer`. The test fails if a `retry` draw is still appended.
- `record_reoffer` on a `timeout` terminal appends no `retry` draw. The test fails if a `retry` draw is still appended.
- `record_reoffer` on a `gate_failed` terminal still appends the `retry` draw. The test fails if the draw is dropped for it.
- `docs/how-chupa-works.md` names `infra_error` and `timeout` among the terminals that draw no `retry` on re-offer; check with `tests/integration/test_drain.py` and a review of that doc line.

## Verification

```
./dev.py test tests/integration/test_drain.py -k reoffer
```

## Regression

```
./dev.py test tests/integration/test_drain.py -k reoffer_rules_and_recording
```

- carries: tests/integration/test_drain.py

## Definition of rejected

Rejected if `abandoned` reaps lose their retry draw, if `runner.py` is touched, or if the new test also passes while `record_reoffer` still draws `retry` for `infra_error`.

## Time budget

- expected: 20m
- stuck: 60m
