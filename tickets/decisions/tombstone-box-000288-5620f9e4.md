---
id: tombstone-box-000288-5620f9e4
kind: tombstone
link: implement-authoring-error-kind
reopen_after_days: 30
---
A retro finding says core-drift-activation's Implement attempts reported a scope-fence omission as kind spec_gap against 19.P6.core-drift-activation, though plan-gap-31 had already added the obligation to that unit. The spec_gap filed plan-gap-32, which came back already_satisfied, and the ticket was parked spec_gap_unresolved. The proposed fix is for the Implement spec to classify a repair that only changes the ticket's fence, Context or criteria as authoring_error, and to check the cited unit on HEAD before reporting spec_gap.

Merged ticket implement-authoring-error-kind covers this same gap. It was filed for the same core-drift-activation incident: fence walls arrived as spec_gap against units that already stated the closure, which caused repeated hardening rounds that ended already_satisfied. That ticket made the Implement spec route a scope fence missing a forced path to authoring_error. Since then, remove-plan-gap-hardening has also merged. The current chupa/specs/implement.md has no spec_gap or kind field. Its premise rule says a scope fence that lacks a path the criteria force is a plain `premise` finding naming that file, so the misclassification path in this message no longer exists.

- Merged ticket tickets/implement-authoring-error-kind/ticket.md Goal: fence walls arrive as `spec_gap` against units that already state the closure: `core-drift-activation` drew six hardening rounds, two ending `already_satisfied`, for two unfenced test files
- git log: 40d9d4da and 3e280b34 chupa(implement-authoring-error-kind) merged
- chupa/specs/implement.md on HEAD has no `spec_gap` or `authoring_error` text; lines 103-104: a ticket whose `## Scope fence` lacks a path the criteria force is a `premise` finding naming that file
- remove-plan-gap-hardening is in the merged list

Message: box-000288-5620f9e4
