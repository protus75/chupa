---
id: decision-box-000041-605fce3c
kind: decision
link: box-000041-605fce3c
reopen_after_days: 60
---
The driver gives every stage run the full `caps.retry` count of in-stage re-prompts (`chupa/driver.py:176`, `:310`; `chupa/requisition.py:134`). Separately, the drain draws one `retry` unit from the journal for each cross-attempt re-offer (`chupa/drain.py:503-505`). So the two retry kinds do not share one budget, and the worst case for a ticket is about (retry+1)×(retry+1) calls, not retry+1. The note asks to pass the journal-derived remaining budget into the driver as a `retries_left` argument.

The split is real in current code, but the extra cost has a fixed ceiling: both `caps.retry` and the drain's journaled draws limit it, and config forces retry to be at most diagnosis. No incident shows harm from it: no runaway spend, no stuck ticket, no wrong outcome. In-stage re-prompts only fix invalid reply shapes, and cross-attempt re-offers fix failed runs, so counting them separately does not cause incorrect behavior. The note is about matching the code to the frozen plan text, plus speculative tightening of spend. The admission bar treats both as a decision unless they are tied to incorrect behavior someone can actually hit.

- chupa/driver.py:176 sets retry_cap=config.caps.retry on every driver build, so each stage run starts with the full count
- chupa/driver.py:310 loops range(1, retry_cap + 2) for in-stage re-prompts
- chupa/requisition.py:134,175 use driver.retry_cap the same way
- chupa/drain.py:503-505 calls caps.consume(..., 'retry', ...) once for each re-offer, and that draw is separate from the in-stage re-prompts
- chupa/config.py:445 requires caps.retry <= caps.diagnosis, so the worst case has a fixed ceiling
- No open ticket, merged stem, or registry decision covers combining the two retry budgets

Message: box-000041-605fce3c
