---
id: tombstone-box-000289-8bfe6a42
kind: tombstone
link: implement-authoring-error-kind
reopen_after_days: 30
---
In core-drift-activation attempts 4 and 5, Implement reported a missing scope-fence entry (tests/test_serve.py) as a spec_gap against 19.P6.core-drift-activation, even though that unit already stated the obligation. The wrong kind filed plan-gap-34, which spent an implement call and two diagnose calls before settling already_satisfied, and it parked the seed in the Reject queue as spec_gap_unresolved. The proposed fix is for implement.md to classify the case where a unit states a fact the ticket omits as kind authoring_error with unit null, quoting the unit text.

This is the same failure and the same implement.md repair as registry record tombstone-box-000288-5620f9e4, which was tombstoned to merged ticket implement-authoring-error-kind. That ticket makes Implement classify a repair that only touches the ticket's fence, Context or criteria as authoring_error, and check the cited unit on HEAD before reporting spec_gap. This message differs only in citing plan-gap-34 and attempts 4-5 instead of plan-gap-32, which are earlier instances of the same class.

- Decision registry tombstone-box-000288-5620f9e4: core-drift-activation fence omission misreported as spec_gap against 19.P6.core-drift-activation; proposed fix classifies fence/Context/criteria-only repairs as authoring_error; linked to implement-authoring-error-kind
- Merged stems list includes implement-authoring-error-kind
- Message proposed_spec_paths is chupa/specs/implement.md, the same surface as the merged ticket

Message: box-000289-8bfe6a42
