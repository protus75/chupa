# Host ticket authoring

What to put in a chupa ticket, and the rules the code cannot explain on its own. The ticket
FORMAT (frontmatter keys, section names, list and block syntax) is owned by `chupa/tickets.py`
alone: start from the skeleton chupa writes and fix what its lint reports. A host's own docs say
what content its tickets carry, never the format.

## Workflow

1. `chupa new <stem>` writes `tickets/<stem>/ticket.md` and lints it. Every finding names the
   fix to apply.
2. Fill each section with the content below, re-lint, and repeat until it is clean.
3. For a bug, add the evidence file (see Bug tickets) beside the ticket.
4. Run `chupa drain`: intake commits the ticket and its evidence together before running it.

## What each section is for

- `Depends on`: tickets that must merge first. Ordering lives here and in `priority`, never in
  prose.
- `Context`: files the implementing agent reads before starting; they are embedded in its prompt.
  They must already exist: a file the ticket creates belongs in `Scope fence` only.
- `On-demand`: existing files the agent may need but that are too large to embed; it reads them
  from its worktree.
- `Goal / Why`: what is true when the ticket is done that is not true now, and why it matters.
- `Scope in / Scope out`: what the agent changes, and what it must leave alone.
- `Scope fence`: every path the agent may write. Fence every file the acceptance criteria force
  it to change, including existing tests whose assertions flip; a forced file outside the fence
  makes the ticket impossible. A ticket that changes documented behavior also fences that
  document and says in `Scope in / Scope out` which part to update, so docs and code land
  together.
- `Acceptance criteria`: each criterion is a check someone can run or a path someone can read,
  never a judgment word.
- `Verification`: the commands Check runs; every one must exit 0.
- `Definition of rejected`: outcomes that mean the branch is thrown away even if it passes.
- `Time budget`: `expected` is your estimate; `stuck` is the deadline that stops the run.

Host tickets omit `Plan contract`; it resolves against chupa's own plan.

## Path matching

A fence entry matches a file when the file IS that path or lives under it as a directory:
`src/app` admits `src/app/views.py` but not `src/application.py`. A string prefix of a name never
matches. The same rule applies to `carries`.

## Bug tickets

A `kind: bug` ticket must prove the defect existed and is fixed. Three things carry the proof.

### Evidence

At least one file under `tickets/<stem>/evidence/`, committed with the ticket before it runs:
the observed wrong output, a log excerpt, or the failing command's captured output. The file
must be a regular, non-symlink file and must not be gitignored. Intake refuses a bug ticket
without such a file, leaving it untouched and uncommitted; when admitted, its new or changed
evidence files are committed with the ticket in the same commit. Settled and rejected tickets
are exempt from this intake check. Supply real evidence, never a placeholder.

### The regression command

`## Regression` names one command, plus the test or fixture paths it carries. The command
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
