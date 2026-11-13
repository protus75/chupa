"""Ticket contract and runner intake.

At invocation, intake lints every pending hand-authored
`tickets/<stem>/ticket.md` and ticket-plane-commits the clean ones, one commit per stem.
"""

import ast
import re
import shlex
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError, field_validator

from chupa.artifacts import Finding, NonBlank
from chupa.covgate import GateInvalid, parse_gate
from chupa.gates import ENGINE_GATE_CODES
from chupa.git import Git, NothingToCommit
from chupa.journal import EventType, Journal
from chupa.seams import FileSystem

TICKETS_DIR = "tickets"
TICKET_FILE = "ticket.md"
STEM = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
RESERVED_STEMS = frozenset({"decisions", "retro"})  # sibling dirs that match the stem regex
INTAKE_SIGNAL = "ticket_intake"
CODE = "ticket_schema"
TEST_FIXTURE_DIRS = frozenset({"tests", "test", "fixtures", "fixture"})

Level = Literal["low", "medium", "high", "max"]
Source = Annotated[str, StringConstraints(pattern=r"^(human|seed|box:[a-z][a-z0-9_]*)$")]


class GateBypass(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    code: NonBlank
    reason: NonBlank

    @field_validator("code")
    @classmethod
    def _known_code(cls, v: str) -> str:
        if v not in ENGINE_GATE_CODES:
            raise ValueError(f"{v!r} is not a gate code; use one of {sorted(ENGINE_GATE_CODES)}")
        return v


class Frontmatter(BaseModel):
    """The closed frontmatter list: only fields the scheduler, a gate, or authoring/triage policy reads."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    state: Literal["draft", "confirmed", "rejected", "merged"]
    source: Source
    priority: Literal["P0", "P1", "P2", "P3"]
    kind: Literal["bug", "feature", "chore"]
    agent_tier: Level = "medium"
    agent_effort: Level = "medium"
    gate_bypass: list[GateBypass] = Field(default_factory=list)


REQUIRED_SECTIONS = (
    "Depends on",
    "Context",
    "Goal / Why",
    "Scope in / Scope out",
    "Scope fence",
    "Acceptance criteria",
    "Verification",
    "Definition of rejected",
    "Time budget",
)
OPTIONAL_SECTIONS = ("Runs before", "On-demand", "Regression")
SECTIONS = REQUIRED_SECTIONS + OPTIONAL_SECTIONS
BANNED_ADJECTIVES = re.compile(r"\b(improved|better|cleaner)\b", re.IGNORECASE)
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_HEADING = re.compile(r"^## (.+?)\s*$")
_ITEM = re.compile(r"^(?:-|\d+\.)\s+(.*)$")
_BUDGET = re.compile(r"^(expected|stuck):\s*(\d+)m$")


@dataclass(frozen=True)
class Ticket:
    stem: str
    frontmatter: Frontmatter
    sections: Mapping[str, str]
    depends: tuple[str, ...]
    context: tuple[str, ...]
    on_demand: tuple[str, ...]
    scope_fence: tuple[str, ...]
    verification: tuple[tuple[str, ...], ...]
    expected_minutes: int
    stuck_minutes: int
    runs_before: tuple[str, ...] = ()
    regression: tuple[str, ...] = ()
    carries: tuple[str, ...] = ()


class TicketInvalid(Exception):
    def __init__(self, findings: list[Finding]) -> None:
        super().__init__("; ".join(f.message for f in findings))
        self.findings = findings


class IntakeRefused(Exception):
    """Intake as a whole cannot commit safely; nothing was committed."""

    def __init__(self, finding: Finding) -> None:
        super().__init__(f"{finding.message} -- {finding.paved_road}")
        self.finding = finding


def ticket_path(stem: str) -> str:
    return f"{TICKETS_DIR}/{stem}/{TICKET_FILE}"


def stem_findings(stem: str) -> list[Finding]:
    path = f"{TICKETS_DIR}/{stem}/"
    if not STEM.fullmatch(stem):
        return [_f(f"stem {stem!r} does not match {STEM.pattern}", "rename the ticket dir to lowercase kebab-case, 2-64 characters, starting with a letter or digit", path)]
    if stem in RESERVED_STEMS:
        return [_f(f"stem {stem!r} is a reserved tickets/ sibling dir", f"pick a stem other than {sorted(RESERVED_STEMS)}", path)]
    return []


def _f(message: str, road: str, path: str | None = None) -> Finding:
    return Finding(code=CODE, path=path, message=message, paved_road=road)


# --- parse --------------------------------------------------------------------------------------


def split_frontmatter(text: str) -> tuple[str, str] | None:
    m = _FRONTMATTER.match(text)
    return (m.group(1), text[m.end() :]) if m else None


def _load_frontmatter(raw: str, path: str) -> tuple[dict | None, list[Finding]]:
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        return None, [_f(f"frontmatter is not valid YAML: {e}", "fix the YAML between the `---` fences", path)]
    if not isinstance(data, dict):
        return None, [_f("frontmatter is not a YAML mapping", "write `key: value` lines between the `---` fences", path)]
    return data, []


def _sections(body: str, path: str) -> tuple[dict[str, str], list[Finding]]:
    sections: dict[str, list[str]] = {}
    findings = []
    current: list[str] | None = None
    fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and (m := _HEADING.match(line)):
            name = m.group(1)
            if name not in SECTIONS:
                findings.append(_f(f"unknown body section `## {name}`", f"use only the allowed sections: {', '.join(SECTIONS)}", path))
            elif name in sections:
                findings.append(_f(f"duplicate body section `## {name}`", "merge the two into one section", path))
            current = sections.setdefault(name, [])
            continue
        if current is not None:
            current.append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}, findings


def _bullets(text: str, name: str, path: str) -> tuple[list[str], list[Finding]]:
    items, findings = [], []
    for line in text.splitlines():
        if not line.strip():
            continue
        if not line.startswith("- "):
            findings.append(_f(f"`## {name}` line {line.strip()!r} is not a `- ` bullet", f"write `## {name}` as one `- ` bullet per entry", path))
            continue
        items.append(line[2:].strip().strip("`").strip())
    return items, findings


def _fenced_commands(text: str, name: str, path: str) -> tuple[list[tuple[str, ...]], list[str], list[Finding]]:
    """One fenced block of argv-parseable commands; returns (commands, the lines outside the fence, findings)."""
    road = f"put the commands in ONE ``` fenced block under `## {name}`, one argv command per line, no shell syntax"
    lines = text.splitlines()
    opens = [i for i, line in enumerate(lines) if line.strip().startswith("```")]
    if len(opens) != 2:
        return [], [], [_f(f"`## {name}` needs exactly one fenced command block", road, path)]
    commands, findings = [], []
    for line in lines[opens[0] + 1 : opens[1]]:
        if not line.strip():
            continue
        try:
            argv = shlex.split(line, posix=True)
        except ValueError as e:
            findings.append(_f(f"`## {name}` command {line!r} is not argv-parseable: {e}", road, path))
            continue
        if not argv or not argv[0].strip():
            findings.append(_f(f"`## {name}` command has no executable", road, path))
            continue
        commands.append(tuple(argv))
    if not commands and not findings:
        findings.append(_f(f"`## {name}` fenced block holds no command", road, path))
    outside = [line for i, line in enumerate(lines) if not opens[0] <= i <= opens[1] and line.strip()]
    return commands, outside, findings


def _repo_path(value: str, name: str, path: str) -> list[Finding]:
    p = Path(value)
    if not value or p.is_absolute() or ".." in p.parts:
        return [_f(f"`## {name}` entry {value!r} is not a repo-relative path", "write a path relative to the repo root, without `..`", path)]
    return []


def context_path(entry: str) -> str:
    return re.split(r"::|#", entry, maxsplit=1)[0]


def context_conflicts(entries: Sequence[str]) -> list[str]:
    whole = {entry for entry in entries if context_path(entry) == entry}
    return sorted(whole & {context_path(entry) for entry in entries if context_path(entry) != entry})


def context_excerpt(entry: str, text: str | None) -> str:
    """Resolve a Context entry against text; validate its extension before text is read."""
    path = context_path(entry)
    selector = entry[len(path) :]
    if not selector:
        return text or ""
    if selector.startswith("::"):
        if Path(path).suffix != ".py":
            raise ValueError("Python selectors require a .py file")
        name = selector[2:]
        if text is None:
            return ""
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            raise ValueError(f"cannot parse Python file: {exc.msg}") from exc
        parts = name.split(".")
        nodes = tree.body
        if len(parts) == 2:
            cls = next((n for n in nodes if isinstance(n, ast.ClassDef) and n.name == parts[0]), None)
            nodes = cls.body if cls else []
        elif len(parts) != 1:
            nodes = []
        matches = [
            n
            for n in nodes
            if (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == parts[-1])
            or (len(parts) == 1 and isinstance(n, ast.ClassDef) and n.name == name)
            or (len(parts) == 1 and isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name)
            or (len(parts) == 1 and isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == name)
        ]
        if len(matches) != 1:
            raise ValueError(f"Python selector {name!r} must match exactly one definition")
        node = matches[0]
        start = min([node.lineno, *(d.lineno for d in getattr(node, "decorator_list", []))])
        return "".join(text.splitlines(keepends=True)[start - 1 : node.end_lineno])
    if Path(path).suffix != ".md":
        raise ValueError("heading selectors require a .md file")
    if text is None:
        return ""
    heading = selector[1:]
    lines = text.splitlines(keepends=True)
    headings = []
    fence = None
    for i, line in enumerate(lines):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not line[marker.end() :].strip():
                fence = None
            continue
        if fence is None and (match := re.match(r"^ {0,3}(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*(?:\r?\n)?$", line)):
            headings.append((i, len(match[1]), match[2]))
    matches = [(i, level) for i, level, title in headings if heading and (title == heading or title.startswith(heading + " "))]
    if len(matches) != 1:
        raise ValueError(f"heading {heading!r} must match exactly one heading")
    start, level = matches[0]
    end = next((i for i, depth, _ in headings if i > start and depth <= level), len(lines))
    return "".join(lines[start:end])


def _criteria(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        if m := _ITEM.match(line):
            items.append(m.group(1))
        elif line.strip() and items:
            items[-1] += " " + line.strip()
        elif line.strip():
            items.append(line.strip())
    return items


def render_context(repo: Path, entry: str) -> str:
    """Read and render one ticket Context entry."""
    return context_excerpt(entry, (repo / context_path(entry)).read_text())


def _parse_ticket(stem: str, text: str, repo: Path, *, evidence: bool) -> Ticket:
    """Validate one ticket against the full ticket grammar; raise TicketInvalid with every finding.

    `repo` resolves `Context` / `On-demand` existence and ordering stems.
    """
    path = ticket_path(stem)
    findings = stem_findings(stem)
    split = split_frontmatter(text)
    if split is None:
        raise TicketInvalid(findings + [_f("ticket.md has no frontmatter", "open the file with a `---` fenced YAML frontmatter block", path)])
    data, errs = _load_frontmatter(split[0], path)
    if data is None:
        raise TicketInvalid(findings + errs)
    fm = None
    try:
        fm = Frontmatter.model_validate(data)
    except ValidationError as e:
        allowed = ", ".join(Frontmatter.model_fields)
        findings += [
            _f(
                f"frontmatter `{'.'.join(map(str, err['loc']))}`: {err['msg']}",
                f"frontmatter carries only {allowed}; fix the value to its closed vocabulary or move non-scheduling detail into the body",
                path,
            )
            for err in e.errors()
        ]

    sections, errs = _sections(split[1], path)
    findings += errs
    for name in REQUIRED_SECTIONS:
        if not sections.get(name):
            findings.append(_f(f"missing or empty body section `## {name}`", f"add a non-empty `## {name}` section", path))

    tickets_root = repo / TICKETS_DIR
    depends: list[str] = []
    if text_ := sections.get("Depends on"):
        items, errs = (["none"], []) if text_.strip() == "none" else _bullets(text_, "Depends on", path)
        findings += errs
        if items != ["none"]:
            for dep in items:
                if dep == stem:
                    findings.append(_f(f"`## Depends on` names the ticket itself ({dep!r})", "drop the self-edge", path))
                elif not STEM.fullmatch(dep) or not ((tickets_root / dep / TICKET_FILE).is_file()):
                    findings.append(_f(f"`## Depends on` stem {dep!r} does not resolve to an existing ticket", f"name an existing `{TICKETS_DIR}/<stem>/` dir, or `none`", path))
                else:
                    depends.append(dep)

    runs_before: list[str] = []
    if "Runs before" in sections:
        items, errs = _bullets(sections["Runs before"], "Runs before", path)
        findings += errs
        if not items:
            findings.append(_f("`## Runs before` has no stems", "list existing ticket stems as bullets, or remove the section", path))
        for target in items:
            if target == stem:
                findings.append(_f(f"`## Runs before` names the ticket itself ({target!r})", "drop the self-edge", path))
            elif target == "none" or not STEM.fullmatch(target) or not (tickets_root / target).is_dir():
                findings.append(_f(f"`## Runs before` stem {target!r} does not resolve to an existing ticket dir", "name an existing `tickets/<stem>/` dir, or remove the section", path))
            else:
                runs_before.append(target)

    context: list[str] = []
    if text_ := sections.get("Context"):
        items, errs = _bullets(text_, "Context", path)
        findings += errs
        for conflict in context_conflicts(items):
            findings.append(_f(f"`## Context` lists {conflict!r} both whole and by section", "list the whole file or its sections, not both", path))
        for item in items:
            source = context_path(item)
            if errs := _repo_path(source, "Context", path):
                findings += errs
            elif Path(source).parent == Path("chupa/specs") and source.endswith(".md"):
                findings.append(_f(f"`## Context` cites the prompt spec {item}; prompt-spec files are never Context", "list the spec under `## On-demand` and fence it", path))
            elif not (repo / source).is_file():
                findings.append(
                    _f(
                        f"`## Context` path {item!r} does not exist as a file",
                        "Context lists EXISTING read-first files; name a file this ticket creates in `## Scope fence` and `## Verification` only",
                        path,
                    )
                )
            else:
                try:
                    context_excerpt(item, None)
                    render_context(repo, item)
                except (ValueError, UnicodeError) as exc:
                    findings.append(
                        _f(
                            f"`## Context` entry {item!r}: {exc}",
                            "select an existing definition or unique heading in a matching file, or list the whole file; "
                            "Context embeds UTF-8 text files only, so name a binary file by path in `## Goal / Why` or `## Scope in / Scope out`",
                            path,
                        )
                    )
                else:
                    context.append(item)

    fence: list[str] = []
    if text_ := sections.get("Scope fence"):
        items, errs = _bullets(text_, "Scope fence", path)
        findings += errs
        for item in items:
            findings += (errs := _repo_path(item, "Scope fence", path))
            if errs:
                continue
            fence.append(item)

    on_demand: list[str] = []
    if text_ := sections.get("On-demand"):
        items, errs = _bullets(text_, "On-demand", path)
        findings += errs
        for item in items:
            if errs := _repo_path(item, "On-demand", path):
                findings += errs
            elif not (repo / item).is_file():
                findings.append(_f(f"`## On-demand` path {item!r} does not exist", "list only EXISTING files the implementer reads from the worktree", path))
            elif not any(item == f or item.startswith(f.rstrip("/") + "/") for f in fence):
                findings.append(_f(f"`## On-demand` path {item!r} is not covered by `## Scope fence`", "fence it, or move a read-only reference to `## Context`", path))
            elif item in {context_path(entry) for entry in context}:
                findings.append(_f(f"`## On-demand` path {item!r} is also in `## Context`", "keep it in exactly one of the two sections", path))
            else:
                on_demand.append(item)

    if text_ := sections.get("Acceptance criteria"):
        if m := BANNED_ADJECTIVES.search(text_):
            findings.append(_f(f"`## Acceptance criteria` uses the unmeasurable adjective {m.group(1)!r}", 'state a measurable outcome ("exits 0 when...", "is unchanged")', path))
        for item in _criteria(text_):
            if "`" not in item:
                findings.append(_f(f"acceptance criterion {item!r} names no check", "name the `## Verification` command or the observable artifact that checks it, in backticks", path))

    commands: list[tuple[str, ...]] = []
    if text_ := sections.get("Verification"):
        commands, outside, errs = _fenced_commands(text_, "Verification", path)
        findings += errs
        if outside:
            findings.append(_f("`## Verification` has text outside its fenced block", "keep only the fenced command block in `## Verification`", path))

    regression, carries = (), ()
    kind = fm.kind if fm is not None else data.get("kind")
    if "Regression" in sections:
        if kind != "bug":
            findings.append(_f("`## Regression` is present on a non-bug ticket", "drop `## Regression`, or set `kind: bug` if this ticket fixes a defect", path))
        regression, carries, errs = _regression(sections["Regression"], path)
        findings += errs
    elif kind == "bug":
        findings.append(_f("a `kind: bug` ticket has no `## Regression` section", "add `## Regression`: one fenced reproducing command plus `- carries: <path-prefix>` bullets", path))

    expected = stuck = 0
    if text_ := sections.get("Time budget"):
        items, errs = _bullets(text_, "Time budget", path)
        findings += errs
        budget = {m.group(1): int(m.group(2)) for item in items if (m := _BUDGET.match(item))}
        if len(items) != 2 or set(budget) != {"expected", "stuck"} or 0 in budget.values():
            findings.append(_f("`## Time budget` is not an expected/stuck minutes pair", "write exactly two bullets, `- expected: <int>m` and `- stuck: <int>m`", path))
        else:
            expected, stuck = budget["expected"], budget["stuck"]
            if stuck <= expected:
                findings.append(_f(f"`## Time budget` stuck: {stuck}m must exceed expected: {expected}m", "set stuck greater than expected (the stage deadline is the stuck budget)", path))

    if findings or fm is None:
        raise TicketInvalid(findings)
    ticket = Ticket(
        stem=stem,
        frontmatter=fm,
        sections=sections,
        depends=tuple(depends),
        context=tuple(context),
        on_demand=tuple(on_demand),
        scope_fence=tuple(fence),
        verification=tuple(commands),
        expected_minutes=expected,
        stuck_minutes=stuck,
        runs_before=tuple(runs_before),
        regression=regression,
        carries=carries,
    )
    if evidence and (findings := evidence_findings(ticket, repo)):
        raise TicketInvalid(findings)
    return ticket


def parse_ticket(stem: str, text: str, repo: Path) -> Ticket:
    return _parse_ticket(stem, text, repo, evidence=True)


def _regression(text: str, path: str) -> tuple[tuple[str, ...], tuple[str, ...], list[Finding]]:
    commands, outside, findings = _fenced_commands(text, "Regression", path)
    if len(commands) > 1:
        findings.append(_f("`## Regression` holds more than one command", "reduce it to the ONE command that reproduces the defect", path))
    carries = [line for line in outside if re.fullmatch(r"- carries: \S+", line.strip())]
    if not carries or len(carries) != len(outside):
        findings.append(
            _f(
                "`## Regression` needs `- carries: <path-prefix>` bullets and nothing else outside the fence",
                "add one `- carries: <path-prefix>` bullet per branch-added test/fixture path the command needs",
                path,
            )
        )
    prefixes = tuple(line.strip().removeprefix("- carries: ") for line in carries)
    for prefix in prefixes:
        findings += _repo_path(prefix, "Regression carries", path)
        if not TEST_FIXTURE_DIRS.intersection(Path(prefix).parts):
            findings.append(_f(f"`## Regression` carries prefix {prefix!r} is not a test/fixture path", "carry a reproducer under `tests/`", path))
    return (commands[0] if len(commands) == 1 else ()), prefixes, findings


def depends_cycle(stem: str, edges: Mapping[str, Sequence[str]]) -> list[str] | None:
    """A dependency path from `stem` back to itself, or None."""
    stack: list[tuple[str, list[str]]] = [(d, [stem, d]) for d in edges.get(stem, ())]
    seen: set[str] = set()
    while stack:
        node, trail = stack.pop()
        if node == stem:
            return trail
        if node in seen:
            continue
        seen.add(node)
        stack += [(d, trail + [d]) for d in edges.get(node, ())]
    return None


def _graph(repo: Path, section: str = "Depends on") -> dict[str, list[str]]:
    """Read each on-disk ticket's named section leniently; a malformed ticket contributes no edges."""
    edges: dict[str, list[str]] = {}
    root = repo / TICKETS_DIR
    for ticket in sorted(root.glob(f"*/{TICKET_FILE}")):
        split = split_frontmatter(ticket.read_text())
        if split is None:
            continue
        sections, _ = _sections(split[1], "")
        items, _ = _bullets(sections.get(section, ""), section, "")
        edges[ticket.parent.name] = [i for i in items if i != "none"]
    return edges


def validate_ticket(stem: str, text: str, repo: Path, *, _settled: bool = False, graphs=None) -> Ticket:
    """The full intake lint: grammar and acyclicity."""
    ticket = _parse_ticket(stem, text, repo, evidence=False) if _settled else parse_ticket(stem, text, repo)
    edges = dict(graphs[0]) if graphs is not None else _graph(repo)
    edges[stem] = list(ticket.depends)
    if cycle := depends_cycle(stem, edges):
        raise TicketInvalid([_f(f"`## Depends on` closes a cycle: {' -> '.join(cycle)}", "drop the edge that inverts the intended order", ticket_path(stem))])
    edges = dict(graphs[1]) if graphs is not None else _graph(repo, "Runs before")
    edges[stem] = list(ticket.runs_before)
    if cycle := depends_cycle(stem, edges):
        raise TicketInvalid([_f(f"`## Runs before` closes a cycle: {' -> '.join(cycle)}", "drop the edge that inverts the intended order", ticket_path(stem))])
    return ticket


# --- intake -------------------------------------------------------------------------------------


def _regular_evidence(path: Path, directory: Path) -> bool:
    return path.is_file() and not any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(directory))


def lint_findings(ticket: Ticket, repo: Path) -> list[Finding]:
    """Decidable authoring rules, separate from scan and merge admission."""
    path = ticket_path(ticket.stem)
    findings = []
    if ticket.regression and not any(
        not Path(arg).is_absolute() and ".." not in Path(arg).parts and any(str(Path(arg)) == prefix.rstrip("/") or str(Path(arg)).startswith(prefix.rstrip("/") + "/") for prefix in ticket.carries)
        for arg in ticket.regression
    ):
        findings.append(
            _f(
                "`## Regression` command does not name a carried file",
                "run a reproducer under a `carries:` prefix; a test runner such as `./dev.py test` or pytest does not speak the regression protocol",
                path,
            )
        )
    for prefix in ticket.carries:
        if not any(prefix.rstrip("/") == fence.rstrip("/") or prefix.startswith(fence.rstrip("/") + "/") for fence in ticket.scope_fence):
            findings.append(_f(f"`## Regression` carries prefix {prefix!r} is outside `## Scope fence`", "add the carried prefix to `## Scope fence`", path))
    gate_path = repo / "test-gate.toml"
    if gate_path.exists():
        try:
            gate = parse_gate(gate_path.read_text())
        except GateInvalid as exc:
            findings.append(_f(f"invalid test-gate.toml: {exc}", "repair test-gate.toml to match the coverage gate schema", "test-gate.toml"))
        else:
            if not any(prefix.startswith("tests/unit/") for prefix in ticket.scope_fence):
                for file, floor in gate.files.items():
                    if floor > 0 and any(file == prefix.rstrip("/") or file.startswith(prefix.rstrip("/") + "/") for prefix in ticket.scope_fence):
                        findings.append(_f(f"fenced file {file!r} has unit coverage floor {floor}", "fence a test file under `tests/unit/` that runs the changed lines", path))
    return findings


def evidence_findings(ticket: Ticket, repo: Path, *, paths: Collection[str] | None = None) -> list[Finding]:
    """Check durable bug evidence; intake supplies only paths it can commit."""
    if ticket.frontmatter.kind != "bug" or ticket.frontmatter.state in {"merged", "rejected"}:
        return []
    return missing_evidence_findings(ticket.stem, repo, paths=paths)


def missing_evidence_findings(stem: str, repo: Path, *, paths: Collection[str] | None = None) -> list[Finding]:
    """Check evidence even while a newly authored bug still has grammar placeholders."""
    directory = repo / TICKETS_DIR / stem / "evidence"
    candidates = directory.rglob("*") if paths is None else (repo / p for p in paths)
    if any(p.is_relative_to(directory) and _regular_evidence(p, directory) for p in candidates):
        return []
    rel = directory.relative_to(repo).as_posix()
    return [
        _f(
            "a `kind: bug` ticket has no evidence file",
            f"add the observed failure (output, log excerpt, or captured command output) as a file under {rel}; the evidence file must not be gitignored",
            rel,
        )
    ]


@dataclass(frozen=True)
class IntakeResult:
    committed: tuple[str, ...]
    refused: Mapping[str, list[Finding]]


def _porcelain(out: str) -> list[tuple[str, str]]:
    entries = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        status, path = line[:2], line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append((status, path.strip('"')))
    return entries


def _pending(repo: Path, entries: list[tuple[str, str]]) -> dict[str, bool]:
    """Pending ticket stem -> True when the stem is NEW (no committed predecessor)."""
    pending: dict[str, bool] = {}
    for status, path in entries:
        if status[1] == "D" or status[0] == "D":
            continue
        new = status == "??" or status[0] == "A"
        if path.endswith("/") and status == "??":
            # An untracked dir collapses its contents into one porcelain line.
            for ticket in (repo / path).glob(f"**/{TICKET_FILE}"):
                rel = ticket.relative_to(repo).as_posix()
                if _is_ticket_path(rel):
                    pending[rel.split("/")[1]] = True
        elif _is_ticket_path(path):
            pending[path.split("/")[1]] = new
    return pending


def _is_ticket_path(path: str) -> bool:
    parts = path.split("/")
    return len(parts) == 3 and parts[0] == TICKETS_DIR and parts[2] == TICKET_FILE


def stamp(text: str, key: str, value: str) -> str:
    """Set one frontmatter key in place, leaving every other line byte-identical."""
    raw, body = split_frontmatter(text)  # type: ignore[misc]
    lines = raw.splitlines()
    line = f"{key}: {value}"
    hits = [i for i, existing in enumerate(lines) if re.match(rf"{key}\s*:", existing)]
    if hits:
        lines[hits[0]] = line
    else:
        lines.append(line)
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def _intake_claims(stem: str, text: str, new: bool) -> tuple[str, list[Finding]]:
    """Apply the fail-closed `source` stamp and the human auto-confirm; return the text to commit."""
    path = ticket_path(stem)
    split = split_frontmatter(text)
    if split is None:
        return text, []  # the grammar lint reports it
    data, errs = _load_frontmatter(split[0], path)
    if data is None:
        return text, errs
    if not new:
        # An established stem keeps the source it was committed with; intake never restamps it.
        return text, []
    source = data.get("source", "human")
    if source != "human":
        return text, [
            _f(
                f"new stem claims `source: {source}`; only the machine writes `seed` or `box:<class>`",
                "drop the `source:` line (intake stamps `source: human`) -- machine-originated work enters through the Suggestion Box",
                path,
            )
        ]
    state = data.get("state", "draft")
    if state not in ("draft", "confirmed"):
        return text, [_f(f"new stem is authored `state: {state}`", "author new work as `state: draft` or `confirmed` (human intake auto-confirms)", path)]
    return stamp(stamp(text, "source", "human"), "state", "confirmed"), []


def _intake_stray(repo: Path, entries: list[tuple[str, str]], evidence: Mapping[str, list[str]]) -> list[str]:
    pending = _pending(repo, entries)
    allowed = {ticket_path(s) for s in pending} | {p for paths in evidence.values() for p in paths}
    return sorted(p for st, p in entries if st[0] not in " ?" and (p not in allowed or "D" in st))


def _intake_plan_stem(repo: Path, stem: str, new: bool, paths: Collection[str], state: str | None, *, graphs=None) -> tuple[str, str, Ticket | list[Finding]]:
    """Read and validate one pending stem without writing or invoking git."""
    text = (repo / ticket_path(stem)).read_text()
    stamped, findings = _intake_claims(stem, text, new)
    try:
        if findings:
            raise TicketInvalid(findings)
        settled = state in {"merged", "already_satisfied", "rejected"}
        kwargs = {"graphs": graphs} if graphs is not None else {}
        ticket = validate_ticket(stem, stamped, repo, _settled=True, **kwargs) if settled else validate_ticket(stem, stamped, repo, **kwargs)
        if not settled and (findings := lint_findings(ticket, repo) + evidence_findings(ticket, repo, paths=paths)):
            raise TicketInvalid(findings)
    except TicketInvalid as exc:
        return text, stamped, exc.findings
    return text, stamped, ticket


async def intake_pending(repo, git, entries):
    """Read the committable evidence and stray paths for one porcelain listing."""
    pending = _pending(repo, entries)
    evidence = {}
    for stem in pending:
        directory = repo / TICKETS_DIR / stem / "evidence"
        paths = await git._run(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", f"{TICKETS_DIR}/{stem}/evidence/")
        evidence[stem] = sorted({p for p in paths.split("\0") if p and _regular_evidence(repo / p, directory)})
    return pending, evidence, _intake_stray(repo, entries, evidence)


async def intake(repo: Path, git: Git, journal: Journal, fs: FileSystem, *, stems: Collection[str] | None) -> IntakeResult:
    """Validate pending hand-authored ticket files and ticket-plane-commit each clean one.

    Intake holds the commit lock across status, the stray check and commits; its git work needs no engine lock.
    A refused ticket stays on disk, uncommitted, untouched.
    """
    async with git._commit_lock:
        entries = _porcelain(await git.status_porcelain(repo))
        pending, evidence, stray = await intake_pending(repo, git, entries)
        if stray:
            from chupa.status import intake_stray_admission

            admission = intake_stray_admission(stray)
            raise IntakeRefused(_f(admission.message, admission.paved_road))
        from chupa.status import last_states

        states = last_states(journal.read())
        committed: list[str] = []
        refused: dict[str, list[Finding]] = {}
        for stem in sorted(pending):
            if stems is not None and stem not in stems:
                continue
            rel = ticket_path(stem)
            text, stamped, decision = _intake_plan_stem(repo, stem, pending[stem], evidence[stem], states.get(stem))
            if isinstance(decision, list):
                refused[stem] = decision
                continue
            fm = decision.frontmatter
            if stamped != text:
                fs.write(repo / rel, stamped.encode())
            paths = [rel, *evidence[stem]]
            # Pathspec-limited: a refused ticket must never ride along in another stem's commit.
            try:
                sha = await git._commit(repo, f"chupa({stem}): ticket", only=paths)
            except NothingToCommit:
                continue
            journal.append(EventType.SIGNAL, {"signal": INTAKE_SIGNAL, "source": fm.source, "state": fm.state, "new": pending[stem], "commit": sha}, ticket=stem)
            committed.append(stem)
        return IntakeResult(committed=tuple(committed), refused=refused)


# --- new ----------------------------------------------------------------------------------------


def order(text: str, *, priority: str | None, runs_before: Sequence[str] | None) -> str:
    """Edit ordering fields without rewriting the rest of the ticket."""
    if priority is not None:
        end = text.index("\n---\n", 4)
        front = text[:end]
        front = re.sub(r"(?m)^(priority\s*:\s*).*$", lambda m: m[1] + priority, front, count=1)
        text = front + text[end:]
    if runs_before is not None:
        headings = []
        offset = 0
        fenced = False
        for line in text.splitlines(keepends=True):
            if line.lstrip().startswith("```"):
                fenced = not fenced
            elif not fenced and (match := _HEADING.match(line.rstrip("\n"))):
                headings.append((match.group(1), offset))
            offset += len(line)
        existing = next((i for i, (name, _) in enumerate(headings) if name == "Runs before"), None)
        if existing is not None:
            start = headings[existing][1]
            end = headings[existing + 1][1] if existing + 1 < len(headings) else len(text)
            section = text[start:end]
            trailing = re.search(r"\n*$", section).group()
            replacement = "## Runs before\n" + "\n".join(f"- {s}" for s in runs_before) + trailing if runs_before else ""
            text = text[:start] + replacement + text[end:]
        elif runs_before:
            i = next(i for i, (name, _) in enumerate(headings) if name == "Depends on")
            end = headings[i + 1][1] if i + 1 < len(headings) else len(text)
            text = text[:end] + "## Runs before\n" + "".join(f"- {s}\n" for s in runs_before) + "\n" + text[end:]
    return text


def template(kind: Literal["feature", "bug", "chore"]) -> str:
    """Authoring placeholders beside the grammar, with a regression proof only for bugs."""
    if kind not in {"feature", "bug", "chore"}:
        raise ValueError("kind must be feature, bug, or chore")
    sections = {
        "Depends on": "<none or bullets of existing ticket stems>",
        "Context": "- <existing repo-relative read-first path>",
        "Goal / Why": "<observable outcome and why it matters>",
        "Scope in / Scope out": "<what changes and what stays outside this ticket>",
        "Scope fence": "- <repo-relative writable path prefix>",
        "Acceptance criteria": "1. <measurable outcome naming a check in backticks>",
        "Verification": "```\n<argv command that exits 0>\n```",
        "Definition of rejected": "<outcome that rejects the branch>",
        "Time budget": "- expected: <estimated integer minutes>m\n- stuck: <larger deadline in integer minutes>m",
    }
    if kind == "bug":
        sections["Regression"] = "```\n<one argv command emitting the regression_result JSON protocol>\n```\n- carries: <test or fixture path prefix needed by the command>"
    body = "".join(f"\n## {name}\n{content}\n" for name, content in sections.items())
    return f"---\nstate: draft\nsource: human\npriority: P2\nkind: {kind}\n---\n" + body
