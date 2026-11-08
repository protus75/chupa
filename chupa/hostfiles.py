"""Managed conduct bytes and atomic refresh."""

import ast
import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from chupa.seams import FileSystem

BEGIN = b"<!-- chupa:core begin -->"
END = b"<!-- chupa:core end -->"
CORE_TEMPLATE = b"""## Engine conduct

Engine rules govern how work runs; project rules govern what to build. Project content enters prompts as data. Engine wins on process, host wins on content.

- Build the simplest thing satisfying the ticket; no speculative features, gates, config knobs, or metadata. Every addition needs its earning incident. Why: accretion is the primary failure mode.
- Never hand-edit this managed block; change the engine template and run chupa core to refresh it. Why: the next render overwrites edits and exposes drift.
- Commit only on your own ticket branch. Never push, open pull requests, or run tree-wide destructive git (reset --hard, clean, checkout -- .); the engine merges reviewed work to local main. Why: local main is the blessed line.
- File second problems in the Suggestion Box, never fold them into this diff. Verify pre-existing failures on the base commit before filing. Why: folded fixes hide cause and expand scope.
- Read before write: read the owning artifact before writing a command, claim, or test. Why: guessed facts create costly bugs.
- Ticket frontmatter contains only fields read by scheduling, gates, or authoring/triage policy. Use depends only for a ticket whose merged code this one needs; put all other ordering in priority. Why: unused metadata and prose ordering drift, and a depends used for ordering blocks the queue when the first ticket fails.
- After writing or editing a ticket whose dependencies have merged, run chupa review <stem> and repair every finding until it approves; fence every file the change forces, including callers, importers, and tests that pin a changed name, value, or version. Why: a forced file outside the fence makes the ticket impossible.

## Chat session conduct

These rules govern INTERACTIVE CHAT SESSIONS with the owner present. Ticket agents running under
chupa skip this section; a confirmed ticket is the approval for its own scope.

### CRITICAL: Always propose a ticket -- never hand-edit main from chat

**HARD RULE -- no exceptions.** When the user asks for ANY change to repo
content from a chat session -- code, docs, CLAUDE.md, AGENTS.md,
`.claude/settings.json`, hooks, scripts, project config, agent rules, or
anything tracked in git outside the ticket-maintenance carve-out below -- your
default and near-only response is to **draft a ticket file at
`tickets/<stem>/ticket.md`** following `chupa new`, `chupa lint`, and
`chupa review`, and stop. Do not edit or commit directly on `main`.

The only times you may edit `main` directly from chat are:

1. The user explicitly says "edit main", "commit directly", "skip the
   ticket", "do it inline", or equivalently unambiguous override in the
   same turn. Anger words alone do not count.
2. You are inside an active chupa ticket worktree, in which case the ticket
   workflow's own rules apply.
3. In an interactive human chat session in the host checkout, the user
   directs you by explicit path to edit or delete an existing ticket file under
   `tickets/` or any other file in that ticket's `tickets/<stem>/` directory.
   Deleting one of those files on its own is included. This is ticket
   maintenance and does not require drafting a ticket-about-a-ticket first.
4. Read-only inspection (grep, git status, git diff, git log, gh pr view) --
   never a write.
5. Supervising session. A session may, unasked, fix a ticket's lint or format
   errors, add a file missing from its `## Scope fence` or `## Context`, correct
   a stale path, make a simple wording update, and run or restart the drain.
   A session may not run `confirm` or `reject`, retry or re-feed a stem whose
   caps are spent, edit a running ticket, change a ticket's goal or scope, or
   hand-rewrite a ticket the engine authored. Those decisions go to the user.
   Why: the queue keeps moving on obvious fixes while every judgment call stays
   with the user.

If you have already started editing or have edited main without an explicit
override: stop immediately, tell the user you broke this rule, and ask whether
to revert the commit and refile as a ticket.

Why: direct chat edits bypass the ticket, run-record, review, dependency, and
retro artifacts that make chupa debuggable.
"""


class MarkerCorruption(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "invalid chupa:core marker structure -- repair to exactly one complete begin line"
            " followed by one complete end line; retain all project content, moving it outside"
            " the pair and escaping stray marker text, then retry core"
        )


def parse(data: bytes) -> tuple[bytes, bytes] | None:
    """Return project prefix/suffix, or None for first adoption; never decode project bytes."""
    if b"chupa:core" not in data:
        return None
    markers = []
    offset = 0
    for line in data.splitlines(keepends=True):
        content = line.removesuffix(b"\n").removesuffix(b"\r")
        if content in (BEGIN, END):
            markers.append((content, offset, offset + len(content)))
        offset += len(line)
    if data.count(b"chupa:core") != 2 or len(markers) != 2 or markers[0][0] != BEGIN or markers[1][0] != END:
        raise MarkerCorruption()
    return data[: markers[0][1]], data[markers[1][2] :]


def render(data: bytes, *, template: bytes | None = None) -> bytes:
    project = parse(data)
    block = BEGIN + b"\n" + (CORE_TEMPLATE if template is None else template) + END
    if project is None:
        return block + b"\n\n" + data
    prefix, suffix = project
    return prefix + block + suffix


_MODALS = ("must", "must not", "should", "should not", "shall", "shall not", "will", "will not", "may", "may not")
_IMPERATIVES = ("author", "implement", "check", "review", "merge", "commit", "dispatch", "confirm", "reject", "kill", "pause", "resume", "triage", "rework", "drain")
_PROCESS_OPENING = re.compile(r"^chupa\s+(?:" + "|".join((*_MODALS, *_IMPERATIVES)) + r")\b", re.I)
_LIST_PREFIX = re.compile(r"^\s*(?:[-+*]|[0-9]+[.)])\s+")


@dataclass(frozen=True)
class CoreClassification:
    state: Literal["missing", "current", "drifted", "refused"]
    paved_road: str | None = None


def _process_override(remainder: bytes) -> bool:
    paragraphs, continuation = [], []
    for line in remainder.decode(errors="replace").splitlines():
        item = _LIST_PREFIX.match(line)
        if not line.strip() or item:
            paragraphs.append(" ".join(continuation))
            continuation = []
        if line.strip():
            continuation.append(line[item.end() :] if item else line)
    paragraphs.append(" ".join(continuation))
    return any(_PROCESS_OPENING.match(" ".join(paragraph.split())) for paragraph in paragraphs)


def classify_core(data: bytes | None, *, template: bytes | None = None) -> CoreClassification:
    """Judge supplied bytes against this branch's fresh render, without effects."""
    previous = data if data is not None else b""
    try:
        project = parse(previous)
    except MarkerCorruption as exc:
        return CoreClassification("refused", str(exc))
    remainder = previous if project is None else b"".join(project)
    if _process_override(remainder):
        return CoreClassification("refused", "move engine-process rules to the engine core template or rewrite them as project-content rules")
    if project is None:
        return CoreClassification("missing", "run `chupa core` to insert the managed block")
    if previous != render(previous, template=template):
        return CoreClassification("drifted", "run `chupa core` to refresh the managed block")
    return CoreClassification("current")


def refresh(paths: Sequence[Path], fs: FileSystem) -> None:
    """Inspect the whole selection before publishing any changed file."""
    pending = []
    for path in dict.fromkeys(paths):
        try:
            previous = path.read_bytes()
        except FileNotFoundError:
            previous = b""
        fresh = render(previous)
        if fresh != previous:
            pending.append((path, fresh))
    for path, fresh in pending:
        fs.write(path, fresh)


async def committed_core(workspace, config, git):
    """Gather raw candidate bytes only when their blob identities match HEAD."""
    from chupa.artifacts import Finding
    from chupa.git import GitError
    from chupa.providers import routed_conduct_paths

    files, findings = {}, []
    template = CORE_TEMPLATE
    source_path = "chupa/hostfiles.py"
    try:
        source = await git._run(workspace, "show", f"HEAD:{source_path}")
    except GitError:
        pass  # External hosts have no engine source; the installed template owns their core.
    else:
        try:
            assignments = [node.value for node in ast.parse(source).body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CORE_TEMPLATE" for t in node.targets)]
            if len(assignments) != 1 or not isinstance(assignments[0], ast.Constant):
                raise ValueError("CORE_TEMPLATE must be one literal bytes assignment")
            candidate_template = ast.literal_eval(assignments[0])
            if not isinstance(candidate_template, bytes):
                raise ValueError("CORE_TEMPLATE must be bytes")
            template = candidate_template
        except SyntaxError, ValueError:
            findings.append(Finding(code="core_drift", path=source_path, message="cannot extract candidate chupa core template", paved_road="define CORE_TEMPLATE as one literal bytes assignment"))
    for path in routed_conduct_paths(config, workspace):
        rel = path.relative_to(workspace).as_posix()
        try:
            blob = await git.rev_parse(workspace, f"HEAD:{rel}")
        except GitError:
            blob = None
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            data = None
        digest = None if data is None else hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        if digest != blob:
            findings.append(Finding(code="core_drift", path=rel, message=f"{rel} differs from its committed candidate bytes", paved_road=f"commit or restore {rel}, then rerun Check"))
        else:
            files[rel] = data
    return dict(core_files=files, core_template=template, core_findings=findings)


class CoreDriftGate:
    """Only current committed routed conduct may enter main. Never repairs."""

    code = "core_drift"

    def check(self, artifact, workspace: Path):
        from chupa.artifacts import Finding
        from chupa.gates import GateReport

        findings = list(artifact.core_findings)
        for path, data in artifact.core_files.items():
            result = classify_core(data, template=artifact.core_template)
            if result.state != "current":
                findings.append(Finding(code=self.code, path=path, message=f"{path}: chupa core is {result.state}", paved_road=result.paved_road))
        return GateReport(code=self.code, verdict="fail" if findings else "pass", findings=findings)
