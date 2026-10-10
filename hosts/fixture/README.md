# Disposable score host

Use `scaffold.copy_host(destination)` to create a fresh disposable host. All five
scripts are declared in `scripts.json`: three distinct prospective machine
merges, an existing add regression and a check-passing spending escape.
These are inputs, not recorded engine merges. The defective settings and the
regression test are both present on the base of a fresh host repository.

Use the chupa venv's Python and the existing process-exec seam with argv lists
`[python, "check.py"]`, `[python, "regression_test.py"]`, and
`[python, "replay.py", "evidence/<scenario>.json"]`. Replay returns 0 for healthy
and 1 for a defect; stdout contains deterministic final state and defect JSON.

For the existing Claude adapter, put the disposable `bin/` first on an explicit
PATH that also contains the chupa venv's Python. Set `CHUPA_FIXTURE_ROOT`,
`CHUPA_FIXTURE_SCENARIO` and `CHUPA_FIXTURE_SURFACE` in the child's environment;
pass no provider keys. Version, pnpm lookup and the stdin preflight probe are
offline. Each scenario has one reply per surface. Unknown selection refuses
with the declared list; exhaustion names the disposable response replenishment
road. Only Implement changes settings.json. Prompts and script cursors reside
in `.fixture-runtime/`, never engine state. Script replies carry no engine
provenance or merge claims. The local tests validate reports directly against
the Records contract, without a future inbox dependency.

The profile's config and conduct file cover the engine safety inventory.
Disposable repository constructors render `CLAUDE.md` with the installed core
renderer and commit it before later production checks. This scaffold does not
start serve, confirm tickets, write journal events, record GO, produce exit
reports or refresh committed fixture inputs. Later host-loop machinery owns
those actions and runtime report production.
