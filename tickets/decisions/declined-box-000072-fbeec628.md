---
id: declined-box-000072-fbeec628
kind: declined
link: box-000072-fbeec628
reopen_after_days: 90
---
A review note says the text of a `ProviderCallError` (decoded event `result` or `turn.failed` message) is scrubbed only in its raw or JSON-escaped form, so the exception object itself can hold a secret. It proposes scrubbing the message in the shared provider base class.

The note says nothing leaks today. The driver Spool and EngineLog, which write the error message out, both run the Redactor again before writing. That makes this defensive hardening of an in-memory object, with no reachable incorrect runtime behavior. Earlier decisions 000008 and 000044 settled the same kind of question: when callers already scrub at the write seam, another scrub layer is not admitted without a demonstrated leak.

- The message states downstream writers (driver Spool, EngineLog) re-scrub the message, so no leak today
- declined-box-000008-cf146223 and declined-box-000044-79b4ca8b declined extra scrub layers because existing write seams already redact
- No failure, incident, or journal/spool/log artifact containing a secret is cited

Message: box-000072-fbeec628
