---
id: tombstone-box-000276-527c50bd
kind: tombstone
link: declined-box-000046-340e80a7
reopen_after_days: 90
---
The note asks for an injectable sleep seam on the runner's Checkout so that driver timeout behavior follows an injected clock. Checkout already has one. `chupa/runner.py:81` declares `sleep: Sleep = asyncio.sleep` as a Checkout field. `bind` and the pipeline pass `checkout.sleep` into `Driver.from_config` (lines 132 and 467), and the re-bind at line 416 passes `ctx.driver.sleep` back into Checkout.

Registry record 000046 already settled this request: `chupa/runner.py` supplies the `Sleep` seam, with `asyncio.sleep` as the production default, to the driver and the other consumers. The current code confirms the seam can be injected through Checkout, so the note shows no gap in current behavior.

- chupa/runner.py:81 `sleep: Sleep = asyncio.sleep` field on Checkout
- chupa/runner.py:132 `Driver.from_config(..., clock=checkout.clock, sleep=checkout.sleep, ...)`
- chupa/runner.py:467 same wiring on the second Driver construction
- chupa/runner.py:416 Checkout rebuilt with `ctx.driver.clock, ctx.driver.sleep`
- Registry declined-box-000046-340e80a7 covers the same Sleep-seam wiring

Message: box-000276-527c50bd
