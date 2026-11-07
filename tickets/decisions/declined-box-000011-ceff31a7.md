---
id: declined-box-000011-ceff31a7
kind: declined
link: box-000011-ceff31a7
reopen_after_days: 60
---
Each `Effects` object reads the journal once when it is created and then keeps its own list of finished effect keys. When one process creates several of them, an object that already exists does not see keys another object finishes later. The note asks for one shared `Effects` per session, created alongside the journal.

The code does create several `Effects` per process: driver, runner, triage, `__main__`, notify, the serve checkpoint, and short-lived ones in control.py, mergequeue.py and serve.py. The gap is real in the code. Harm needs two of these objects to run the same effect key, with the long-lived one created before the other records the key as finished. No evidence shows that happens. Each caller uses its own keys (control-inbox actions, merge receipts, serve baselines, checkpoint pushes, notifications, stage effects). The short-lived objects re-read the journal every time they are built, so they always see current state. No run record shows an effect running twice or a wrong replay. Without a demonstrated incident this is speculative hardening, the same kind of note as decision-box-000010 (two calls with the same key in flight at once).

- chupa/effects.py:21 builds `_completed` from one journal read at construction; line 46 adds keys only to that object's own set
- Effects( is constructed at chupa/control.py:260, mergequeue.py:369, runner.py:131/446, driver.py:141, __main__.py:515, notify.py:116, triage.py:110/134, serve.py:346/517
- control.py, mergequeue.py and serve.py:346 construct a fresh instance per call and re-read the journal each time
- No failure report, run record or bug report shows an effect running twice across instances
- Related decision-box-000010-e476a678 deferred `Effects` key-guard hardening until a concurrent caller exists

Message: box-000011-ceff31a7
