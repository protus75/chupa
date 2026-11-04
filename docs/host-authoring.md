# Host ticket authoring

How to write a ticket chupa accepts. This guide owns the ticket FORMAT: sections, frontmatter,
list syntax, Verification and Regression syntax, the bug evidence protocol, and the time budget.
Project rules (which docs to cite, which commands to verify with, which paths are off limits)
belong to the host and live in the host's own docs; a host doc names a section here and says
what goes in it, never restates its syntax.

Authority: `chupa/tickets.py` is the grammar (intake lint), `chupa/stages.py` runs the gates.
Where this guide and the code disagree, the code wins and this guide is fixed.

## Workflow

1. `chupa new <stem>` writes `tickets/<stem>/ticket.md` with every required section empty and
   lints it; the findings list what to fill. Or copy a template below.
2. Fill every section. For `kind: bug`, start from the bug template.
3. The ticket must pass `chupa.tickets.validate_ticket` (the intake lint `chupa new`, `run` and
   `drain` apply). A read-only `chupa lint` verb is planned (`19.P8.lint-verb`); until it ships,
   hosts call `validate_ticket` from a small wrapper script.
4. Commit the ticket file; `chupa drain` runs committed tickets only.

Every lint finding carries a paved road: the fix to apply.

## Stem

`tickets/<stem>/ticket.md`, stem matching `^[a-z0-9][a-z0-9-]{1,63}$`. `decisions` and `retro`
are reserved. A stem is used once: write new work under a new stem.

## Frontmatter

YAML between `---` fences. Only these keys; any other key is refused.

| Key | Values | Default |
|---|---|---|
| `state` | `draft`, `confirmed` (new tickets); `rejected`, `merged` are machine-written | required |
| `source` | `human` for hand-authored tickets; `seed`, `box:<class>` are machine-only | required |
| `priority` | `P0`, `P1`, `P2`, `P3` | required |
| `kind` | `feature`, `bug`, `chore` | required |
| `agent_tier` | `low`, `medium`, `high`, `max` | `medium` |
| `agent_effort` | `low`, `medium`, `high`, `max` | `medium` |
| `gate_bypass` | list of `{code, reason}`, `code` an engine gate code | `[]` |

Intake stamps a new hand-authored stem `source: human` and `state: confirmed`. Ordering lives in
`## Depends on` and `priority`, never in prose or extra keys.

## Body sections

Only these `##` headings are accepted; an unknown or duplicate heading is refused.

Required, each non-empty: `Depends on`, `Context`, `Goal / Why`, `Scope in / Scope out`,
`Scope fence`, `Acceptance criteria`, `Verification`, `Definition of rejected`, `Time budget`.

Optional: `On-demand`; `Regression` (exactly when `kind: bug`). `Plan contract` and
`Exit-read window` are engine-internal (they resolve against chupa's own plan); host tickets
omit them.

Free-text sections (`Goal / Why`, `Scope in / Scope out`, `Definition of rejected`) may use `###`
subsections and any prose.

### `## Depends on`

`none` alone, or one `- <stem>` bullet per predecessor. Each stem must be an existing ticket;
no self-edge; no cycle. A ticket dispatches only after every predecessor has merged.

### `## Context`

One `- <path>` bullet per file the implementing agent reads first. Paths are repo-relative (no
leading `/`, no `..`) and must exist when the ticket is linted; a file the ticket creates goes in
`## Scope fence`, not here. Context files are embedded in the implement prompt.

### `## On-demand`

Optional. `- <path>` bullets for existing fenced files too large to embed; the agent reads them
from the worktree. Each must exist, be covered by `## Scope fence`, and not also be in Context.

### `## Scope fence`

One `- <path>` bullet per writable path. A bullet ending in `/` is a directory and admits
everything under it; a bullet without `/` admits exactly that file or, if it names a directory,
everything under it. A string prefix of a file name does not match (`tests/test_a` does not admit
`tests/test_ab.py`). The scope fence gate fails a branch that changes any file outside the fence.

Fence every file the acceptance criteria force the agent to change, including existing tests
whose assertions the change flips. A criteria-forced file outside the fence makes the ticket
unsatisfiable.

### `## Acceptance criteria`

List items (`- ` or `1.`). Every criterion contains at least one backticked check: an exact
substring of a `## Verification` command or an observable repository path. The words
`improved`, `better` and `cleaner` are refused; state the measurable outcome.

### `## Verification`

Exactly one fenced code block and nothing else in the section. One command per line, parsed as
an argv list (POSIX shell quoting): no pipes, `&&`, redirection, `#` comments, or `VAR=value`
prefixes. Every command must exit 0 for the ticket to pass Check and merge.

### `## Time budget`

Exactly two bullets, `- expected: <int>m` and `- stuck: <int>m`, both above 0, stuck greater
than expected. Stuck is the stage deadline. A ticket whose stuck exceeds the host's
`drain.max_ticket_minutes` is never dispatched: split it.

## Bug tickets

`kind: bug` requires `## Regression`; a non-bug ticket must not have one.

### `## Regression` grammar

Exactly one fenced block holding ONE command, then one or more `- carries: <path-prefix>` bullets,
and nothing else. Each carries prefix is repo-relative and must match at least one file the
branch adds or changes, and every matched file must live under a `tests/`, `test/`, `fixtures/`
or `fixture/` directory: implementation files are never carried.

### Result protocol

The regression command writes exactly one JSON object to stdout and nothing else:
`{"regression_result": "pass"}`, `{"regression_result": "defect"}` or
`{"regression_result": "error"}`. Extra keys, duplicate keys, several objects, other output on
stdout, or unknown values are refused. Diagnostics go to stderr.

- `pass` must come with exit 0.
- `defect` must come with a positive exit.
- `error` means the run could not decide (a missing prerequisite); it never passes.

A bare test runner (`pytest -q`) does not speak the protocol. Write a small carried reproducer
under a test directory that checks its prerequisites, exercises the defect, and prints the
result object.

### How the gate proves the defect

Check runs the command twice: on the branch head (must be exit 0 and `pass`) and on the merge
base with the carried files copied over it (must be a positive exit and `defect`). A test added
with the fix is therefore run against the old code, so a test that merely passes proves nothing,
and a reproducer that fails at base only because its own input is missing does not count.

### Durable evidence

At least one file under `tickets/<stem>/evidence/` (for example the failing command's captured
output). The author commits it with the ticket, before the run; the implementing agent does not
need to write under `tickets/`.

## Feature template

````markdown
---
state: confirmed
source: human
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
none

## Context
- path/to/governing/doc.md
- path/to/module/to/read.py

## Goal / Why
<Observable outcome: what is true when this is done that is not true now.>

<Motivation: the rule or doc section this implements.>

## Scope in / Scope out
### Scope in
- <what the agent changes>

### Scope out
- <what it must not touch>

## Scope fence
- path/to/module.py
- tests/test_module.py

## Acceptance criteria
- `tests/test_module.py` asserts <exact condition>
- `tests/test_module.py` asserts <negative condition>
- `<test command>` passes

## Verification
```bash
<test command>
<lint command>
```

## Definition of rejected
- <condition that means stop and throw the branch away>

## Time budget
- expected: 45m
- stuck: 90m
````

## Bug template

Same as the feature template with `kind: bug`, a `## Regression` section, and an evidence file
committed at `tickets/<stem>/evidence/`. The `Goal / Why` subsections are a suggested shape.

````markdown
---
state: confirmed
source: human
priority: P1
kind: bug
agent_tier: medium
agent_effort: medium
---

## Depends on
none

## Context
- path/to/module/with/defect.py
- tickets/<stem>/evidence/observed.txt

## Goal / Why
<Observable correct behavior after the fix.>

### Root-cause hypothesis
- Suspected location: <file / function>
- Alternative locations to rule out: <at least one>
- Smoking-gun evidence: `tickets/<stem>/evidence/observed.txt`

### Observed vs. expected behavior
Observed: <exact wrong output and the command that shows it>.

Expected: <correct behavior and the spec it comes from>.

## Scope in / Scope out
### Scope in
- the fix in path/to/module/with/defect.py
- tests/test_defect.py (regular tests)
- tests/regress_defect.py (the carried reproducer; prints only the result object)

### Scope out
- every file under `tickets/`

## Scope fence
- path/to/module/with/defect.py
- tests/test_defect.py
- tests/regress_defect.py

## Acceptance criteria
- `python tests/regress_defect.py` prints exactly `{"regression_result": "pass"}` and exits 0
- `tests/test_defect.py` asserts <the corrected behavior>
- `<test command>` passes

## Verification
```bash
python tests/regress_defect.py
<test command>
```

## Regression
```bash
python tests/regress_defect.py
```
- carries: tests/regress_defect.py

## Definition of rejected
- edits, deletes or regenerates any file under `tickets/`
- the reproducer prints anything to stdout besides the result object

## Time budget
- expected: 20m
- stuck: 40m
````
