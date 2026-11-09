---
id: declined-box-000097-cd50f4c0
kind: declined
link: box-000097-cd50f4c0
reopen_after_days: 60
---
In `chupa/__main__.py`, `main` turns only a fixed list of refusal exceptions into exit 2 (lines 498-504). Any other exception, such as a `GitError` from `describe`, an `OSError`, or a `ValueError` from the stage seam, escapes as a Python traceback with exit 1. Under the section 18 contract, exit 1 means a ticket ended in a non-ok terminal state, so a crash and a failed ticket return the same code. The note proposes mapping unexpected engine exceptions to exit 2 or to a separate crash path.

The overlap is real in current code, but nothing is harmed by it. No engine code or extension code tells exit 1 apart from exit 2 for `run` or `drain`. A search of `chupa/` and `vscode-chupa/` for returncode or exit-code checks finds only the gate runner and the exec seam, and neither reads the run verb's exit class. Drain runs tickets in-process, not by reading a child's exit code. A crash also prints a traceback, so an operator cannot mistake it for a ticket outcome. Without a consumer that misreads the code, this is contract tidiness and speculative hardening, not a reachable incorrect runtime behavior.

- chupa/__main__.py:498-504 catches only UnknownBoxId and the named refusal tuple (ConfigError, Refusal, LockHeld, IntakeRefused, JournalCorruption, ProviderSetupError, ExecutableNotFound, MarkerCorruption) and maps them to EXIT_REFUSED; all other exceptions propagate.
- chupa/__main__.py:862 `sys.exit(main())` gives an uncaught exception Python's default exit 1.
- Searching chupa/**/*.py and vscode-chupa for returncode or exit-code checks finds no consumer of the run or drain verb's exit class (only __main__.py:305 gate runner and seams.py:165).

Message: box-000097-cd50f4c0
