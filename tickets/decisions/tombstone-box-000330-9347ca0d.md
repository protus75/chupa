---
id: tombstone-box-000330-9347ca0d
kind: tombstone
link: implement-spec-sequential-final-run
reopen_after_days: 30
---
Implement started full `./dev.py test` runs while it was still editing files under `chupa/`. `tests/test_fixture_host.py::test_fixture_scaffold_is_dormant` snapshots those bytes, so the run went red and had to be repeated. This was recorded in stats-command attempt 1, coverage-map and extension-thin-wrapper attempt 0. The proposed repair adds a rule to `chupa/specs/implement.md`: use focused test runs while editing, then run the full Verification suite once after all edits are finished.

Open ticket implement-spec-sequential-final-run already rewrites this part of `chupa/specs/implement.md` step 3. It requires one final full pass of the Verification commands, run one at a time with nothing else running, and the implementer reports that result. It keeps parallel work allowed outside that final pass and adds no repeated full-suite reruns. This finding asks for the same thing: a final full run with nothing changing underneath it. Another process running at the same time and a file edit landing during the run are two forms of the same rule, so this belongs in that ticket rather than a second ticket on the same spec step. The harm reported here is also smaller. Each case cost one repeated run that the agent fixed itself, and no merge failed because of it.

- Retro finding names stats-command attempt 1, coverage-map, and extension-thin-wrapper attempt 0 as full-suite runs that went red because a file changed during the run
- Open ticket implement-spec-sequential-final-run changes the same `chupa/specs/implement.md` step 3 to require one final full Verification pass, one command at a time, with nothing else running
- Both proposals keep parallel or focused runs allowed while working and limit the new rule to the final full-suite run
- Proposed spec path is `chupa/specs/implement.md`, the same file that ticket edits

Message: box-000330-9347ca0d
