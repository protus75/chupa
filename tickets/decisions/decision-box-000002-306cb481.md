---
id: decision-box-000002-306cb481
kind: decision
link: box-000002-306cb481
reopen_after_days: 90
---
A bootstrap note says the scaffold test checks that the dependency names are present but not their minimum versions. It proposes recording this gap in case a later gate assumes the version floors are tested.

This only asks for better test coverage. No runtime behavior is wrong today, and no gate is shown to rely on tested version floors. The note itself says the current check is fine for its purpose. Under the admission bar that makes it a decision, not an author. It is not a duplicate: no open or merged ticket and no registry entry covers version floors in the scaffold test. Reopen if a gate or check is found to assume the declared floors are enforced, or if a dependency below a declared floor causes a runtime failure.

- The message says the name-only check is fine for a harness proof and is noted only as a caution.
- The message cites no runtime failure or harmful behavior.
- No open ticket, merged stem, or decision covers dependency version floors in tests/test_scaffold.py.

Message: box-000002-306cb481
