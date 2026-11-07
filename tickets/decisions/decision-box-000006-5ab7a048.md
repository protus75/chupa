---
id: decision-box-000006-5ab7a048
kind: decision
link: box-000006-5ab7a048
reopen_after_days: 60
---
The journal writer serializes event bodies to JSON without checking that the reader gets the same value back. A dict with integer keys, for example, comes back with string keys. The note itself calls this harmless today and expects per-type body validation at the write seam to remove it.

No current harmful runtime behavior is shown. The source note says the gap is harmless now, and no evidence shows any engine caller writing a body that changes on round trip (such as integer dict keys) or any reader acting wrongly on one. This is speculative hardening of the write seam. It is close to decision-box-000003-8007f56c, which deferred body validation at the same seam for lack of a bad body ever being written, but it is a different check: round-trip fidelity, not vocabulary.

- Message summary states the gap is 'harmless now'.
- decision-box-000003-8007f56c deferred journal body validation at the write seam because no bad body has ever been written.
- No open or merged ticket adds per-type body validation or round-trip checks to the journal writer.

Message: box-000006-5ab7a048
