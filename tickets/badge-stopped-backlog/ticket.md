---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Runs before
- chupa-ruff-reclean
- chupa-ruff-reclean-tests-a-l

## Context
- chupa/observe.py
- tests/integration/test_watch.py

## On-demand
- docs/how-chupa-works.md

## Goal / Why
The extension's Activity Bar badge shows the queued and running ticket count only while the engine is alive; when the engine is stopped there is no badge, so the operator cannot see from the Activity Bar that un-merged work is waiting for a drain or serve. After this change, while the engine is stopped the snapshot's `badge` carries the blocked plus queued ticket count with a tooltip naming the stopped engine, and stays `None` when that count is 0. The alive behaviour is unchanged. VS Code's `ViewBadge` has only `value` and `tooltip` and draws only a total above 0 in the theme's single badge color, so the count and tooltip are the only signal available; the extension already draws `snap.badge` as given and needs no change.

## Scope in / Scope out
- In: `chupa/observe.py` badge expression in the snapshot builder:
  - alive and `counts["queued"] + counts["running"]` > 0: unchanged, `{"value": queued + running, "tooltip": "<running> running, <queued> queued"}`.
  - not alive and `counts["blocked"] + counts["queued"]` > 0: `{"value": blocked + queued, "tooltip": "engine stopped: <blocked> blocked, <queued> queued"}`.
  - otherwise `None`.
- In: `tests/integration/test_watch.py` `test_snapshot_badge`: replace the dead-engine assertion `badge is None` with the stopped badge `{"value": 2, "tooltip": "engine stopped: 1 blocked, 1 queued"}` for the existing fixture (the `running_stems` stub keeps `live` in the running section, which the stopped badge must not count), and add a dead-engine case with no tickets asserting `badge is None`.
- In: `docs/how-chupa-works.md` the sentence "Its Activity Bar badge shows the queued and running ticket count while the engine is alive and the count is nonzero." becomes a sentence that also states the stopped case (blocked plus queued count, hidden at 0).
- Out: `vscode-chupa/` (it draws `snap.badge` unchanged), the `counts` field, section classification, every other snapshot field.

## Scope fence
- chupa/observe.py
- tests/integration/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. With the engine dead and one blocked plus one queued ticket, `snapshot(ctx)["badge"]` has value equal to blocked + queued and a tooltip starting `engine stopped: `, not `None`; checked by `./dev.py test tests/integration/test_watch.py -k snapshot_badge`.
2. With the engine dead and no blocked or queued tickets, `snapshot(ctx)["badge"]` is `None`, not `{"value": 0, ...}`; checked by `./dev.py test tests/integration/test_watch.py -k snapshot_badge`.
3. With the engine alive, the badge is still `{"value": 2, "tooltip": "1 running, 1 queued"}` for the existing fixture, and blocked rows are not counted; checked by `./dev.py test tests/integration/test_watch.py -k snapshot_badge`.
4. `docs/how-chupa-works.md` states the stopped-engine badge (blocked plus queued count, hidden at 0).
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_watch.py -k snapshot_badge
./dev.py test
```

## Definition of rejected
The alive badge value or tooltip changes; merged or running rows count toward the stopped badge; a zero-valued badge is emitted; any file under `vscode-chupa/` changes.

## Time budget
- expected: 15m
- stuck: 45m
