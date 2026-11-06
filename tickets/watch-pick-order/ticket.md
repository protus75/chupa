---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- watch.py
- chupa/drain.py
- chupa/scheduler.py
- chupa/control.py

## On-demand
- tests/test_drain.py
- tests/test_scheduler.py
- docs/how-chupa-works.md

## Goal / Why
`watch` lists the queue sorted by priority and then stem (`watch.py` `queue`). The engine picks by `order_tickets` (`chupa/drain.py`): priority, then authored age, then stem, with `## Runs before` hints applied. So the queue an operator reads is not the order work runs in, and it never shows a hint. `watch.py` is stdlib-only and cannot import chupa, and copying the ordering into it would be a second implementation.

After this change the engine records the order it computed at each pick, and `watch` shows that order.

## Scope in / Scope out
- In: `chupa/drain.py` `_select` and `chupa/scheduler.py`'s pick: right after `order_tickets` runs, write `state_dir/queue.json` through the filesystem seam.
  - The file holds `{"at": <clock ts>, "order": [stems in pick order], "runs_before": {stem: [named stems]}}`.
  - It is written atomically, as `control/active.json` is.
  - One helper beside `order_tickets` writes it, and both pickers call that helper.
  - The file is a derived view, never read by the engine.
- In: `watch.py` `queue`: when `queue.json` exists, list eligible tickets in its `order`, each line showing `runs before: <stems>` when it has hints. Then list the remaining confirmed tickets with their existing "waits on" or "held" reasons. With no `queue.json`, keep today's listing.
- In: tests.
  - `tests/test_drain.py` and `tests/test_scheduler.py`: after a pick, `queue.json` `order` equals `order_tickets` output, including a `Runs before` case.
  - `tests/test_watch.py` (new): `watch.queue` renders a fixture `queue.json` in its order with the hint text, and falls back without one.
- In: `docs/how-chupa-works.md` sections 10.1 (state files: `queue.json`) and 7.1 (watch shows pick order).
- Out: the ordering itself; eligibility; `status`; serve's merge queue.

## Scope fence
- watch.py
- chupa/drain.py
- chupa/scheduler.py
- tests/test_drain.py
- tests/test_scheduler.py
- tests/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. After the drain picks, `state_dir/queue.json` `order` equals `order_tickets` over the same eligible set. A `Runs before` hint moves the hinting ticket ahead in both. Checked by `uv run pytest tests/test_drain.py`.
2. The serve scheduler writes the same file at each pick, with the same content rules. Checked by `uv run pytest tests/test_scheduler.py`.
3. `watch.queue` lists eligible stems in `queue.json` order with `runs before:` text, then the blocked or held ones. Without the file it falls back to the old listing. Checked by `uv run pytest tests/test_watch.py`.
4. `docs/how-chupa-works.md` sections 7.1 and 10.1 name `queue.json`.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_drain.py tests/test_scheduler.py tests/test_watch.py
uv run pytest -q
```

## Definition of rejected
Ordering logic copied into `watch.py`; the engine reading `queue.json`; two writers of the file; `watch.py` importing chupa or leaving the standard library.

## Time budget
- expected: 45m
- stuck: 120m
