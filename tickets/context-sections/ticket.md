---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/tickets.py
- tests/integration/test_tickets.py
- tests/integration/test_requisition.py
- tests/integration/test_author.py
- docs/host-authoring.md

## On-demand
- chupa/stages.py
- chupa/specs/author.md
- docs/how-chupa-works.md

## Goal / Why
A `## Context` entry embeds its whole file in the Implement prompt. `retro-request-serve` needed one method from `chupa/runner.py`, three functions from `chupa/retro.py`, and two sections of `docs/how-chupa-works.md`, but its eight whole files rendered 328,574 characters. That is over the 300,000-character authoring headroom, so `chupa review` refused it (2026-11-08). A ticket that needs part of a large file has no way to embed only that part.

After this change a `## Context` entry may name one section of a file. A Python file names a top-level definition or a class method; a Markdown file names a heading. The render embeds only that section. A section that does not resolve is a lint finding, so a renamed definition fails closed at intake and at every scan instead of embedding the wrong text.

## Scope in / Scope out
- In: `chupa/tickets.py`, the `## Context` parse in `parse_ticket`.
  - An entry is either a bare path (the whole file, as now) or a path plus one selector.
  - `path::Name` applies only to `.py` files. `Name` is a top-level `def`, `async def`, or `class`, or an assignment whose single target is that name. `Class.method` names a `def` or `async def` directly in that top-level class body. It resolves with `ast` over the file at `repo`.
  - `path#Heading` applies only to `.md` files. It matches the ATX heading whose text equals `Heading` or starts with `Heading` followed by a space (so `#7.2` matches `### 7.2 Implement`).
  - Each of these is a finding with a paved road: a selector on another extension; a name or heading that matches nothing; a heading that matches more than one line; and a file listed both whole and by section.
  - The existing checks (repo-relative path, file exists, not a prompt spec) apply to the path part.
  - Add one function that returns a resolved entry's excerpt, used by both the lint and the render, so the two cannot disagree.
- In: `chupa/stages.py` `implement_inputs`. A section entry renders as `### path::Name` or `### path#Heading` followed by the excerpt. A Python excerpt runs from its first decorator line through `end_lineno`. A Markdown excerpt runs from the heading line up to the next heading of the same or higher level, or end of file. Entries render in listed order. `config.context_files` stays whole-file.
- In: `chupa/specs/author.md`. The `## Context` sentence allows the section forms. Bump its `version` minor.
- In: `docs/host-authoring.md` (the `Context` bullet) and `docs/how-chupa-works.md` section 4.2 describe the section forms.
- In: tests in `tests/integration/test_tickets.py` and `tests/integration/test_requisition.py`.
- In: `tests/integration/test_author.py`: its pin of the author spec version (line 23) and its assertion on the `## Context` sentence (line 33) follow the new `chupa/specs/author.md`.
- Out:
  - `## On-demand`, `## Scope fence`, and `config.context_files` keep whole-path entries;
  - line-number or start/stop ranges;
  - selectors for any file type other than `.py` and `.md`;
  - `chupa/specs/rework.md` and every other spec.

## Scope fence
- chupa/tickets.py
- chupa/stages.py
- chupa/specs/author.md
- tests/integration/test_tickets.py
- tests/integration/test_requisition.py
- tests/integration/test_author.py
- docs/host-authoring.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/integration/test_requisition.py::test_context_section_renders_only_the_section` passes. A ticket whose Context lists `m.py::B.run` and `d.md#Two`, over fixtures where `m.py` has a decorated method `B.run` beside another method and `d.md` has headings `# One`, `## Two`, `### Two-a`, `## Three`, renders:
   - the decorator and body of `B.run` and not the other method or the rest of the file;
   - `## Two` through `### Two-a`, and not `# One` or `## Three`.
   It rules out embedding the whole file, dropping the decorator, and stopping the Markdown excerpt at the subheading.
2. `tests/integration/test_tickets.py::test_context_section_findings` passes. Each of these yields exactly one finding: `m.py::Missing`; `m.py#Two`; `d.md::B`; `d.md#Nope`; a file with two `## Two` headings selected by `#Two`; and `m.py` listed both whole and as `m.py::B.run`. It rules out silently embedding nothing or the whole file for an unresolved selector.
3. `tests/integration/test_tickets.py::test_context_whole_file_unchanged` passes: a bare-path Context entry renders the whole file under `### path`, exactly as before.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_tickets.py tests/integration/test_requisition.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- an unresolved selector renders anything, or passes lint;
- the lint and the render resolve a selector through different code;
- the change adds line-number ranges, a config key, or selectors outside `## Context`.

## Time budget
- expected: 90m
- stuck: 180m
