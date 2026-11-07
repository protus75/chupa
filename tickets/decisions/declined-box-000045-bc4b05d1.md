---
id: declined-box-000045-bc4b05d1
kind: declined
link: box-000045-bc4b05d1
reopen_after_days: 90
---
`EngineLog` in `chupa/enginelog.py` writes its lines with a raw `open(path, "ab")`, not through the FileSystem seam. The seam has no append verb, only atomic write and replace. `journal.py` sets the same precedent. Attempt spools already go through `seams.LocalFileSystem`. The note proposes adding an append verb only when a fake-driven engine-log test needs one.

This is a gap in test seams, not a runtime defect. The raw append writes the engine log correctly, and nothing shows wrong behavior or a test blocked by the missing verb. Decisions 000017 (lockfile raw os/fcntl) and 000025 (config raw read_text) kept the same deferral for other modules: add the seam verb when a fake-driven test needs it.

- chupa/enginelog.py:32 uses `with open(self.path, "ab")`, as the note says
- decision-box-000017-e78ba696 and decision-box-000025-cf8cefbd deferred similar seam-bypass notes until a fake-driven test needs the verb
- no open ticket or failure report shows an engine-log test or behavior blocked by the missing append verb

Message: box-000045-bc4b05d1
