# Host ticket authoring

What to put in a chupa ticket, and the rules the code cannot explain on its own. The ticket
FORMAT (frontmatter keys, section names, list and block syntax) is owned by `chupa/tickets.py`
alone: start from the skeleton chupa writes and fix what its lint reports. A host's own docs say
what content its tickets carry, never the format. See the [host run guide](host-running.md) for invocation and operation.

## Workflow

1. Start with `chupa new <stem> --kind feature|bug|chore`, choosing one kind (default `feature`).
   For a bug, first save the observed failure to a file and pass it with `--evidence <file>`.
   In this repo, use `./dev.py new STEM [--kind K] [--evidence FILE...]`. It writes
   `tickets/<stem>/ticket.md` with section placeholders and lints it. Every finding names the fix
   to apply. A bug includes `## Regression` and copies the evidence files into the ticket.
2. Fill each section with the content below, run `chupa lint <stem>`, and repeat until it is
   clean. In this repo, use `./dev.py lint [STEM...]`. Omit stems to check all tickets that are
   not settled or rejected in the journal (all tickets when there is no journal). In a linked
   worktree, lint with no stems uses the main checkout's journal. Lint applies
   intake's claims and evidence checks without taking the lock or writing anything; it prints
   findings with fixes and a valid/total summary. Exit 0 means all valid, 1 means findings, and
   2 means a named ticket is missing or the tickets directory is unreadable.
3. Before review, check that no criterion contradicts merged behavior or an existing test outside
   the fence, and that all criteria can hold together. Check that every invariant the ticket states
   or cites has a criterion whose test fails when the invariant is dropped.
   Run `chupa review <stem>` (in this repo, `./dev.py review STEM`), repair every finding,
   and repeat until it prints `approve`. Reviews with unmerged dependencies are provisional and not
   journaled; repair their findings, and the drain reviews again after the dependencies merge.
4. A running `serve` picks up the new ticket; alternatively run `chupa drain`. Intake commits
   the ticket and its evidence together before running it.

## What each section is for

- `Depends on`: tickets whose merged code this ticket needs. Use it only for that: a failed
  dependency blocks every ticket behind it. Merged code includes a test helper, fixture, fixture
  data set, or check rule another ticket creates. A ticket that uses one depends on the ticket that creates it.
- `Runs before`: stems this ticket runs ahead of when both are eligible. This soft order never
  blocks; use it, not `Depends on`, for any other ordering. Use `chupa order` to change it or priority.
- `Context`: files the implementing agent reads before starting; they are embedded in its prompt.
  They must be existing UTF-8 text files; lint renders each entry exactly as Implement does.
  A file the ticket creates belongs in `Scope fence` only; name binary files by path in
  `Goal / Why` or `Scope in / Scope out`. Select a Python
  top-level definition, assignment, or class method with `path.py::Name` or `path.py::Class.method`;
  select a Markdown heading with `path.md#Heading` (a heading beginning with that text and a space
  also matches). A selection must resolve uniquely; list a file whole or by sections, not both.
- `On-demand`: existing files the agent may need but that are too large to embed; it reads them
  from its worktree.
- `Goal / Why`: what is true when the ticket is done that is not true now, and why it matters.
- `Scope in / Scope out`: what the agent changes, and what it must leave alone. When Scope in
  limits changes in a fenced file with "only" or "nothing else changes", it names every edit the change forces there.
  Include an import a new name needs and the expected set or skip list of every test that loops
  over a registry the ticket extends.
- `Scope fence`: every path the agent may write. Fence every file the acceptance criteria force
  it to change, including existing tests whose assertions flip; a forced file outside the fence
  makes the ticket impossible. Before replying, grep the repo for each changed name or value.
  When Scope in adds, removes, renames, or moves a member of a set (CLI subcommand, file or directory path, spec name), grep `tests/` and `docs/` for files that list that set or hardcode the old path, and fence every hit that asserts against the changed set or hardcodes the moved path. A mere textual mention, a path built under `tmp_path`, or a historical form the ticket keeps valid is not a hit. A ticket that changes documented behavior also fences that
  document and says in `Scope in / Scope out` which part to update, so docs and code land
  together. A ticket that bumps a prompt spec's `version` states it as the next minor above the version on main,
  never a literal target such as `3.4 -> 3.5`, and fences a test pin for the bumped file.
  Lint requires every carried prefix to be fenced. When a fenced file has a positive
  `[coverage.files]` floor in `test-gate.toml`, lint requires a fenced path under `tests/unit/`.
  When a `Depends on` ticket is not merged yet, the author reads its fence and criteria. Fence
  any test it creates that asserts behavior this ticket changes, and Scope in names the one expectation that may change.
- `Acceptance criteria`: each criterion is a check someone can run or a path someone can read,
  never a judgment word. A criterion checked by a test names the wrong result the test rules out,
  for example, `parse('')` returns `[]`, not `None`. A test that also passes on the wrong result
  checks nothing. Before writing a criterion, check any case that must come from real code, such
  as a loader, builder, or test helper, in that code. A case the code filters out or cannot build
  is marked hand-built with its reason, and the Goal does not promise it.
- `Verification`: the commands Check runs; every one must exit 0.
- `Definition of rejected`: outcomes that mean the branch is thrown away even if it passes.
- `Time budget`: `expected` is your estimate; `stuck` is the deadline that stops the run.

## Path matching

A fence entry matches a file when the file IS that path or lives under it as a directory:
`src/app` admits `src/app/views.py` but not `src/application.py`. A string prefix of a name never
matches. The same rule applies to `carries`.

## Bug tickets

A `kind: bug` ticket must prove the defect existed and is fixed. Three things carry the proof.

### Evidence

`new` copies the supplied files into `tickets/<stem>/evidence/`. At least one file there must be
committed with the ticket before it runs:
the observed wrong output, a log excerpt, or the failing command's captured output. The file
must be a regular, non-symlink file. Every ticket read (intake, lint, confirm, drain, serve, run,
and Author) refuses a bug without evidence. Intake and lint also require evidence that is not
gitignored; intake commits new or changed evidence with the ticket. Settled and rejected tickets
are exempt, including at intake when the journal records settlement. Supply real evidence, never a placeholder.
Save the evidence before any change that destroys it, such as deleting a file, reloading data, or a manual fix.

### The regression command

`## Regression` names one command, plus the test or fixture paths it carries. The command
must name a path under a `carries:` prefix; lint checks this before review. It
prints exactly one JSON object to stdout and nothing else; diagnostics go to stderr.

- `{"regression_result": "pass"}` with exit 0: the defect is absent.
- `{"regression_result": "defect"}` with a non-zero exit: the defect is present.
- `{"regression_result": "error"}`: the run could not decide, for example a missing prerequisite.
  It never counts as either.

Any other stdout, extra keys, or a result whose exit code disagrees is refused. A bare test
runner (`pytest -q`) does not speak this protocol: write a small reproducer under a test or
fixture directory that checks its prerequisites, exercises the defect, and prints the object.

### How Check proves it

Check runs the regression command twice:

1. On the branch head: it must print `pass` and exit 0.
2. On the merge base, with the carried files copied over it: it must print `defect` and exit
   non-zero.

So the reproducer added with the fix is run against the old code. A reproducer that fails at
base only because its own inputs are missing proves nothing; have it check those inputs and
report `error`. Only files under a `tests/`, `test/`, `fixtures/`, or `fixture/` directory can be
carried; implementation files never are.
