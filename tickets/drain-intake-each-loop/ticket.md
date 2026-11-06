---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/drain.py
- chupa/tickets.py
- chupa/serve.py
- tests/test_drain.py
- docs/how-chupa-works.md

## Goal / Why
`drain` runs intake once at startup (`chupa/drain.py`, before `_Drain.run`). A ticket written or edited in the working tree while a drain runs is ignored until the next drain start. This includes a new ticket, a changed `priority:`, or a changed `## Runs before`. `serve`'s watcher runs intake on every scan, so the same edit takes effect within seconds there. The operator reorders queued tickets mid-drain (by hand, or with the `order` verb) and expects the next pick to honor it (2026-11-06).

After this change, `drain` also runs intake between tickets: at the top of each `_Drain.run` loop iteration, before `_scan`. That is never during a ticket's run.

## Scope in / Scope out
- In: `chupa/drain.py`: `_Drain.run` calls `intake(self.c.repo, self.c.git, self.c.journal, self.c.fs)` at the top of each loop iteration, after the stop check and before `_scan`. The startup intake stays.
- In: a per-ticket intake finding behaves as it does at startup: the file stays uncommitted and the drain continues. An `IntakeRefused` (staged changes outside pending ticket files) ends the drain exactly as the startup intake's refusal does.
- In: tests in `tests/test_drain.py`.
  - `test_drain_intakes_ticket_written_mid_drain`: a fake dispatch writes a new confirmed ticket file while running the first ticket. The same drain commits it (`chupa(<stem>): ticket`) and runs it. Two assertions check that intake waits for the run to end:
    - inside the hook, after writing, porcelain still shows the file as `??`;
    - after the drain, the new stem's `ticket_intake` journal event comes after the first ticket's terminal `state_transition`.
  - `test_drain_mid_drain_intake_refusal_exits_2`: while the first of two tickets runs, a hook stages a non-ticket file (`git add` of a new `chupa/stray.py`). `drain` returns 2, `script.calls` holds only the first stem, and the lock is free afterwards.
  - `test_drain_honors_priority_edit_mid_drain`: with three queued tickets, a fake dispatch raises the third's priority while running the first. The next pick is the third.
  - Rewrite `test_an_uncommitted_ticket_file_is_not_eligible`. Today it asserts that a valid ticket written mid-drain never runs, the old behavior. Its hook instead writes a mid-drain ticket that fails lint. Assert that the file stays uncommitted, the ticket never runs (`script.calls == ["seeder"]`), and the drain still exits normally.
- In: `docs/how-chupa-works.md` section 7.1: step 1 keeps "runs intake once" as the startup intake, and step 2 adds "runs intake" to the loop.
- Out: `serve`, intake itself, `run`, and the pick order.

## Scope fence
- chupa/drain.py
- tests/test_drain.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest -q tests/test_drain.py` exits 0, including both tests above.
2. `docs/how-chupa-works.md` section 7.1 says drain runs intake between tickets.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if intake runs while a ticket's stages run, if a ticket written mid-drain waits for the next drain start, if a per-ticket intake finding stops the drain, or if `serve` changes.

## Time budget
- expected: 40m
- stuck: 120m
