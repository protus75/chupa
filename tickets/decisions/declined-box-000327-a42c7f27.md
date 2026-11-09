---
id: declined-box-000327-a42c7f27
kind: declined
link: box-000327-a42c7f27
reopen_after_days: 30
---
The engine filed a depends-stage failure report saying `pypi-package` was blocked because its dependency `specs-in-package` had been rejected or abandoned. It asked for the dependency to be re-wired, the ticket re-scoped, or the ticket rejected. `pypi-package` is now in the merged set, so the block no longer holds anything back.

The dependent this report concerns has already landed. `pypi-package` is merged, so no ticket is blocked waiting on `specs-in-package`, and nothing needs re-wiring, re-scoping or rejecting. `specs-in-package` is still an open ticket and goes through the queue on its own. Its outcome is not tied to this report. Record 000321 settled the same situation for a different pair: the dependent merged, so no failure was left to repair. This report has no reachable runtime failure that one bounded ticket could fix.

- `pypi-package` appears in the merged stems list.
- `specs-in-package` appears in the open tickets list, so it is neither merged nor retired.
- Registry record declined-box-000321-cda44a53 declined a `depends` failure report because its dependent later merged and no failure was left.
- Tombstone record tombstone-box-000001-a8df16f3 already credits merged `pypi-package` with the packaging work.

Message: box-000327-a42c7f27
