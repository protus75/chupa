---
id: tombstone-box-000420-2118c8d8
kind: tombstone
link: declined-box-000418-0758c804
reopen_after_days: 30
---
A note from the verb-lock-need-single-source Implement run says README.md wrongly claims that `review` always takes the writer lock, even though committed tickets that have not changed can be reviewed without it. The run left README.md alone because the file was outside its scope fence.

This is the same report already settled as declined-box-000418-0758c804, and tombstone-box-000419-4ee493b9 already pointed a repeat of it to that record. Both came from the same origin run. On current main, README.md does not say that `review` takes the writer lock. The only lock line, line 73, says `serve` must be stopped before `drain` or `run`, because each of those takes the writer lock. There is no wrong runtime behavior here and no false statement in the docs. Reopen if README.md ever does say that `review` always takes the writer lock.

- README.md:73 reads: 'Stop `serve` before `drain` or `run`: each takes the writer lock.' `review` is not mentioned.
- No other line in README.md mentions the lock (checked with a grep for 'lock').
- declined-box-000418-0758c804 already declined the same README claim.
- tombstone-box-000419-4ee493b9 already tombstoned a repeat of this report from the same verb-lock-need-single-source run, linking to 000418.

Message: box-000420-2118c8d8
