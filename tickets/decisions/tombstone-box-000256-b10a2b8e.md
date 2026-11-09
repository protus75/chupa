---
id: tombstone-box-000256-b10a2b8e
kind: tombstone
link: declined-box-000149-ee537f6f
reopen_after_days: 30
---
When the drain upgrades itself, it restarts as a new `drain --parked` process. The note worries that if the original drain was started with `--config <path>`, the new process would use the default config instead, which could point to a different state directory and lock. It asks section 18 to say whether the restart passes `--config` along, or to refuse the restart when a non-default config is in use.

Registry record declined-box-000149-ee537f6f already decided the same bootstrap note, which raised this exact `--config` concern for the self-upgrade restart. That record found that current code already passes `--config` to the new drain process, so the problem no longer exists.

- Registry record declined-box-000149-ee537f6f covers the same concern: a drain started with `--config` restarting on the default config after a self-upgrade.
- That record says current code already passes `--config` to the new drain process.
- This message comes from the same bootstrap-ingest source and adds no new failure.

Message: box-000256-b10a2b8e
