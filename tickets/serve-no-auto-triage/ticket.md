---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/serve.py
- chupa/triage.py
- chupa/daemon.py
- tests/test_serve.py
- tests/test_provider_cooldown_failover.py
- docs/how-chupa-works.md

## Goal / Why
`serve` triages the Suggestion Box by itself: its box consumer (`Serve.triage`) runs `triage.triage_pass` whenever a message is pending. That spends a model call per message, and it can author tickets nobody asked for. The operator decided (2026-11-06) that nothing triages unless the operator runs `triage`. Automatic triage may come back later as its own refined, tested feature; this ticket only removes it.

After this change `serve`'s box consumer still ingests host bug reports from `report_inbox` into the box, but it never triages. Pending messages stay pending until the operator runs `chupa triage`.

## Scope in / Scope out
- In: `chupa/serve.py`:
  - rename `Serve.triage` to `Serve.box_intake`, and update the `DaemonTasks(box_consumer=...)` wiring;
  - its poll runs `triage.report_intake` under `self.mutations()` as it does now, and nothing else: no `ProviderLLM`, no preflight, no `triage_pass`;
  - `Serve.abort` drops the `self.control.author_driver` branch, since nothing in serve sets it any more.
- In: `chupa/triage.py`: `triage_pass` stops setting and clearing `checkout.control.author_driver`. Only serve read it; the CLI `triage` runs with no control.
- In: `chupa/daemon.py`: remove the `author_driver` attribute.
- In: `tests/test_serve.py`:
  - `test_empty_box_report_intake`: the ingested report stays `pending`, and the journal has no `triage_pass` signal (0, not 1).
  - `test_report_consumer_is_sequential`: becomes a test that both inbox reports are ingested as pending messages with no `triage` surface call. The heartbeat and three-consumer assertions stay.
  - The five-merge test that enqueues `a policy decision`: its wait condition no longer requires a triage call, and it asserts the message is still pending and the `triage` surface was never called.
  - `test_serve_author_uses_shared_journal` is deleted: serve no longer triages or authors.
  - The consumer-ending test's `rig.owner.triage` becomes `rig.owner.box_intake`.
  - `test_serve_failed_notify_backoff_and_restart`: drop the `wait_until(lambda: not rig.owner.box.pending())` line and its comment, since serve no longer settles the storm reports; assert instead that the storm `failure_report` messages are still pending.
- In: `tests/test_provider_cooldown_failover.py`, the test that starts `cli.build_serve` after a drain: remove its serve-triage block (the `triage_pass` stub, the `box.pending` monkeypatches, the `refreshed` wait, and the `c-live` config assertions). Keep its drain and serve provider-session and timer assertions.
- In: `eval/daemon_soak.py`: `file_fault` stops waiting for serve to empty the pending box; it waits until the enqueued message is pending and nothing is mutating. The box-consumer evidence check expects the filed fault reports to be pending and no `triage_pass` signal, instead of requiring a `triage_pass` signal.
- In: `tests/test_daemon_soak_runner.py`: assert the soak's merge `failure_report` messages stay `pending`, not `resolved`.
- In: `eval/host_loop.py`: after the fixture enqueues a suggestion or drops a report into the inbox, it runs the operator `triage` command itself (`python -m chupa triage` through its exec seam, same cwd and env as `serve`) once the message is pending, then waits for the ticket as now. `serve` gains no triage path.
- In: `tests/test_host_loop.py`: update only what the harness change forces.
- In: `docs/how-chupa-works.md`:
  - section 7.2: the fourth loop is **Box intake**, which ingests host bug reports into the Suggestion Box and never triages;
  - section 9.2: only the `triage` command triages; drop "(or `serve`'s triage loop)".
- Out:
  - the `triage` CLI verb and `triage_pass`'s settling behavior;
  - `DaemonTasks` and the heartbeat's consumer slots (the slot keeps its `box_consumer` name);
  - `drain`, which never triaged;
  - any new automatic triage, schedule, or config key.

## Scope fence
- chupa/serve.py
- chupa/triage.py
- chupa/daemon.py
- tests/test_serve.py
- tests/test_provider_cooldown_failover.py
- eval/daemon_soak.py
- tests/test_daemon_soak_runner.py
- eval/host_loop.py
- tests/test_host_loop.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/test_serve.py` exits 0, including `test_empty_box_report_intake`: the report stays pending with 0 `triage_pass` signals, not resolved by a pass.
2. `grep -n "triage_pass\|ProviderLLM\|author_driver" chupa/serve.py` prints nothing.
3. `grep -rn "author_driver" chupa/` prints nothing.
4. `docs/how-chupa-works.md` sections 7.2 and 9.2 say serve does not triage.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_serve.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `serve` or `drain` can still start a triage pass or a `triage` surface call;
- `serve` stops ingesting `report_inbox` reports;
- the `triage` CLI verb's behavior changes;
- a config key, flag, or schedule for triage is added.

## Time budget
- expected: 30m
- stuck: 90m
