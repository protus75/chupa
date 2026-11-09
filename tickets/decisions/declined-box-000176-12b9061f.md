---
id: declined-box-000176-12b9061f
kind: declined
link: box-000176-12b9061f
reopen_after_days: 90
---
A bootstrap handoff note records that the merged `box-start-policy` ticket moved `baseline_identity` and the `review_baseline` signal name from `eval/harness.py` into `chupa/policy.py`, because engine code cannot import `eval/`. It asks frozen-plan unit 19.P2 to name `chupa/policy.py` as the module that owns the baseline identity.

This asks only for plan wording to change, and no runtime behavior is wrong. The code already matches what the note describes. `chupa/policy.py` defines `BASELINE_SIGNAL` and `baseline_identity`, and `eval/harness.py` imports both from there. `CHUPA_PLAN.md` is frozen and never edited, so the requested plan change cannot be made.

- chupa/policy.py:13 defines BASELINE_SIGNAL = "review_baseline"
- chupa/policy.py:19 defines baseline_identity(config, specs_dir)
- eval/harness.py:36 imports BASELINE_SIGNAL and baseline_identity from chupa.policy
- box-start-policy is merged
- CLAUDE.md: CHUPA_PLAN.md is a frozen bootstrap design record and is never edited

Message: box-000176-12b9061f
