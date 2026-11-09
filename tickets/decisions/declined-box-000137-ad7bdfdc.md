---
id: declined-box-000137-ad7bdfdc
kind: declined
link: box-000137-ad7bdfdc
reopen_after_days: 30
---
Author could not produce a ticket.

Evidence: - coverage_floor: test-gate.toml lists "chupa/drain.py" = 10 under [coverage.files]. Scope in adds statements and branches to record_reoffer: a no-retry branch for infra_error, timeout and abandoned, and an infra draw for abandoned. The fence holds only tests/integration files. No tests/unit file imports chupa.drain today, so no named unit test runs the new lines. (do instead: Add tests/unit/test_drain.py to the Scope fence. Add Scope-in and acceptance-criterion lines naming a unit test, for example test_record_reoffer_infra_terminals, that calls record_reoffer with an in-memory journal fake and SimpleNamespace events, the same shape test_reoffer_rules_and_recording uses. It must cover the gate_failed, infra_error, timeout and abandoned branches. Add `./dev.py test tests/unit/test_drain.py` to ## Verification.)
- coverage_dependent_clearance: The test_shakeout.py clearance says the suite has one retry count (eval/shakeout/drain.py:107). eval/shakeout/runner.py:50 (premise_false) and eval/shakeout/stages.py:202 (base_diff_attribution) also count retry draws. eval/shakeout/runner.py _timeout_dead_ends re-offers a timeout terminal. The conclusion still holds: both extra counts assert zero retries on paths that never re-offer an infra terminal, and the timeout member asserts no cap counts. The stated reason is still factually wrong. (do instead: Rewrite the test_shakeout.py clearance sentence. It should say that eval/shakeout/drain.py:107 counts a gate_failed re-offer, that runner.py:50 and stages.py:202 assert zero retry draws on premise and first-pass paths, and that the timeout_dead_ends member re-offers a timeout terminal but asserts no cap counts, so fewer draws change no assertion.)
