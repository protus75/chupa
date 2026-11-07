---
id: declined-box-000058-efb3b19a
kind: declined
link: box-000058-efb3b19a
reopen_after_days: 90
---
A bootstrap review note says the crash-fault harness simulates only process death, so it treats bytes already handed to `os.write` as surviving a crash at the next `fsync`. It does not simulate losing unsynced bytes in a power failure. The note asks for the harness docstring to name this fault model so that a passing run is not read as proof of power-loss safety.

This asks for a docstring change to test code. It reports no runtime failure and no wrong engine behavior. Unclear test documentation does not meet the bar for authoring a ticket, because no engine behavior would change and there is nothing to measure after the change. It matches record declined-box-000057-dfbd681c, which declined a request to extend the same harness's coverage.

- Message class is suggestion with origin bootstrap-ingest. It has no stage, outcome, or failure report.
- The request is a docstring wording change in the crash-fault test harness and does not change engine behavior.
- Registry record declined-box-000057-dfbd681c declined a coverage extension to the same crash-fault harness, also because it reported no failure.
- No open or merged ticket covers modeling of the harness's fault model.

Message: box-000058-efb3b19a
