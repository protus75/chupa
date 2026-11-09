---
id: declined-box-000321-cda44a53
kind: declined
link: box-000321-cda44a53
reopen_after_days: 30
---
A `depends` failure report says ticket stop-at-boundary was blocked because its dependency serve-self-upgrade had been rejected or abandoned. Both stems are now in the merged set, so the dependency settled and the dependent landed. No current failure is left to repair.

The report describes a dependency block that has since cleared. The merged list contains serve-self-upgrade, so the dependency eventually merged after the rejection or abandonment the report saw. It also contains stop-at-boundary, so the dependent was not left stranded. With nothing left to re-wire, re-scope or reject, there is no reachable incorrect runtime behavior and no bounded repair to author. Neither stem appears in the open tickets or the registry, so this is not a tombstone.

- Merged stems include `serve-self-upgrade`
- Merged stems include `stop-at-boundary`
- Message: class failure_report, origin stop-at-boundary, stage depends, outcome rejected
- No open ticket or registry record names stop-at-boundary or serve-self-upgrade

Message: box-000321-cda44a53
