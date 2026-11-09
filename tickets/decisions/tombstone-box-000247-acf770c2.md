---
id: tombstone-box-000247-acf770c2
kind: tombstone
link: tombstone-box-000125-0504c04e
reopen_after_days: 90
---
This is a status note saying the production `runner.pipeline` binding behind `run <stem>` no longer refuses. It now chains the provider LLM, Driver, stages and merge, with `runner.bind` as the test seam. If the provider layer cannot be built, it raises ProviderSetupError and exits 2 before taking the lock. The note reports a resolved state and names no new gap.

This message says the same thing as registry record tombstone-box-000125-0504c04e: the pipeline binding no longer refuses, `runner.bind` is the test seam, and provider setup failure exits 2 before the lock. That record links to declined-box-000095-a9ffd3fe, which already notes that the composition exists. No harmful behavior gap is shown.

- tombstone-box-000125-0504c04e covers the same note: the binding composes provider LLM, driver, stages and merge, with runner.bind as the test seam, and exits 2 before the lock when the provider layer cannot be built
- declined-box-000095-a9ffd3fe records that the production runner.pipeline composition now exists and no longer refuses
- tombstone-box-000113-5d377ece covers the earlier refusing state that this note marks as resolved

Message: box-000247-acf770c2
