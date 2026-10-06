## Outcome

premise_failed

## Surprises / judgment calls

`bind()` in chupa/runner.py wires Driver to raw asyncio.sleep, so the Bench clock advance cannot wake Driver.race() while FakeLLM HANG is active.

## Dead ends

Verified the driver-group command on the untouched branch; it exits 2 because GROUPS contains only stages, and the required timeout fixture would otherwise wait the real 20-minute timer.

## Second problems filed

- box-000276-527c50bd: The runner/Checkout composition needs an injectable sleep seam so driver timeout behavior can follow the injected clock.

## Resolved engine/model

- provider: codex
- model: gpt-5.6-terra
- spec: implement 1.1

## Predicted vs actual

45m predicted; stopped early after confirming the out-of-scope seam gap.

