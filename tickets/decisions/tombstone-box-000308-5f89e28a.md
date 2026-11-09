---
id: tombstone-box-000308-5f89e28a
kind: tombstone
link: declined-box-000307-356acaee
reopen_after_days: 30
---
The `attempts-cap` Implement run reports that the standalone premise-release scenario in `eval/shakeout/drain.py` passes on the base commit but fails when `premise_bounce` is 1. The scenario needs its own explicit budget override, and `eval/` was outside that ticket's fence.

Registry record declined-box-000307-356acaee already decided this report. It came from the same `attempts-cap` Implement run and says the standalone premise-park-release shakeout member in `eval/` must set its own `premise_bounce` budget instead of relying on the config default, with `eval/` outside the fence. This message adds only the base-versus-`premise_bounce=1` framing. It names no new runtime behavior, and the `attempts-cap` ticket has since merged.

- Message origin is `attempts-cap`, stage `implement`, outcome `ok`, the same source as declined-box-000307-356acaee.
- declined-box-000307-356acaee: the standalone `premise_park_release` shakeout member in `eval/` needs its own `premise_bounce` budget, and `eval/` was outside the attempts-cap fence.
- `attempts-cap` appears in the merged stems list.

Message: box-000308-5f89e28a
