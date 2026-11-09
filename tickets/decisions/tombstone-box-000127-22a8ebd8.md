---
id: tombstone-box-000127-22a8ebd8
kind: tombstone
link: terminal-test-config-import
reopen_after_days: 90
---
A review note says tests/test_terminal.py builds its config.yaml by splitting the source text of tests/test_stages.py on the `CONFIG = """` marker. It proposes importing `CONFIG` from tests.test_stages instead, since the file already imports other helpers from there.

The merged ticket `terminal-test-config-import` has a name that matches this change exactly: making the terminal tests import the stages test config instead of parsing source text. I did not open that ticket to confirm its contents. Even without a duplicate, this is a test-only cleanup with no wrong runtime behavior, so it would not meet the bar for authoring.

- The merged stems list includes `terminal-test-config-import`.
- The message names only test files (tests/test_terminal.py, tests/test_stages.py) and reports no runtime failure.

Message: box-000127-22a8ebd8
