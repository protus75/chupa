---
id: declined-box-000146-bd19e063
kind: declined
link: box-000146-bd19e063
reopen_after_days: 60
---
A bootstrap re-entry review note says no test checks the rule that `lift_outbox` skips an outbox artifact whose bytes match the canonical copy already on main. It asks for a unit test showing that an unchanged inherited `review.md` is not committed and a changed one is.

This only adds a test. The note reports no wrong runtime behavior: the byte-equal skip already exists and works, as registry record declined-box-000121-840b47d6 confirmed. A test-only improvement with no reachable incorrect behavior does not meet the admission bar. The open ticket outbox-lift-named-artifact-only is already rewriting the `_lift_files` filtering, so this skip can be pinned there if that change puts it at risk.

- Message class is suggestion, origin bootstrap-ingest; it proposes only a unit test and reports no failure.
- declined-box-000121-840b47d6 records that `_lift_files` in `chupa/stages.py` drops outbox files byte-equal to their canonical copy, and `lift_outbox` returns None when nothing remains.
- Open ticket outbox-lift-named-artifact-only already changes the `lift_outbox`/`_lift_files` filter surface.

Message: box-000146-bd19e063
