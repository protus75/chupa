---
id: declined-box-000438-a10669cb
kind: declined
link: box-000438-a10669cb
reopen_after_days: 30
---
Three verb-level snapshot tests in tests/integration/test_watch.py (lines 176, 194 and 686) take about 18 seconds each. They copy the real config.yaml and run `main(["--config", ..., "snapshot"])` against the live developer checkout, so their cost grows with the number of tickets and git history in the repo. The proposal is to point them at a minimal tmp_path git repo, or to monkeypatch the ticket and git readers.

This is a test-speed and test-isolation improvement only. It describes no wrong runtime behavior in chupa: the tests pass, the snapshot verb gives correct output, and the only cost is suite wall time. The admission bar declines test-only improvements unless they are tied to reachable incorrect runtime behavior. Records 000392 and 000395 declined the same kind of finding about slow integration tests. The O(N²) per-stem snapshot cost the finding cites is a product performance concern raised in menu-table-run-review-admission review; this test rewrite would hide that cost rather than fix it. Reopen if these tests start failing or flaking because of live-checkout content, or if their run time pushes the integration suite past a check timeout or the stuck budget so that tickets fail Check.

- tests/integration/test_watch.py:176-191 copies the real config.yaml and runs main(['--config', ..., 'snapshot']), asserting only configPath, stateDir and one steps row.
- tests/integration/test_watch.py:194-215 runs the snapshot and watch --once verbs against the live checkout and asserts only that the state dir is unchanged plus one output line.
- The message reports passing tests at about 18s each and suite wall times of 65-103s. It names no failed run, timeout or incorrect output.
- Precedent: declined-box-000392-7c3e7668 and declined-box-000395-70ebe69b declined retro findings about slow integration tests as test-only improvements.
- No open or merged ticket covers this exact rewrite, so tombstone does not apply.

Message: box-000438-a10669cb
