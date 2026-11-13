"""Read-only host observations for the CLI and extension."""

import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import get_args

from chupa.config import load_config
from chupa.drain import RETIRED, authored_at, awaiting_operator, order_tickets, parked_blob
from chupa.graph import layout
from chupa.lockfile import ENGINE_VERBS
from chupa.rework import settled_dependencies
from chupa.status import SETTLED, verdict_refusal
from chupa.tickets import Frontmatter, TicketInvalid, parse_ticket

STEP_NAMES = {
    "requisition_review": "Requisition",
    "implement": "Implement",
    "check": "Check",
    "merge": "Merge",
    "review": "Review",
    "diagnose": "Diagnose",
    "rework": "Rework",
    "retro": "Retro",
    "triage": "Triage",
    "author": "Author",
}

PHASE_NAMES = {"preflight": "Preflight", "retro_check": "Retro check"}

STEP_KINDS: dict[str, str] = {
    **{f"{step}_{suffix}": step for step in (*STEP_NAMES, *PHASE_NAMES, "stage") for suffix in ("start", "ok", "failed")},
    **{event: event for event in ("engine_start", "engine_stop", "engine_lost")},
}


@dataclass(frozen=True)
class Context:
    root: Path
    state: Path
    config: Path
    exec: object
    git: object
    env: object


def process_output(ctx, *args):
    _, out, _ = asyncio.run(ctx.exec.run(args, cwd=ctx.root, env=ctx.env, timeout=30))
    return out


def git_output(ctx, *args):
    return asyncio.run(ctx.git._run(ctx.root, *args))


def local(ts: str) -> datetime:
    return datetime.fromisoformat(ts).astimezone()


def clock(ts: str) -> str:
    return local(ts).strftime("%-I:%M %p")


def ago(ts: str) -> str:
    seconds = int((datetime.now().astimezone() - local(ts)).total_seconds())
    return f"{seconds // 60}m{seconds % 60:02d}s"


def relative(ts: str, now: datetime) -> str:
    minutes = int((now - local(ts)).total_seconds() / 60 + 0.5)
    if minutes < 60:
        return f"{minutes} min ago"
    if minutes < 2880:
        return f"{int(minutes / 60 + 0.5)} hr ago"
    return f"{int(minutes / 1440 + 0.5)} days ago"


def processes(ctx) -> list[tuple[int, int, str]]:
    out = process_output(ctx, "ps", "-eo", "pid=,ppid=,args=")
    rows = []
    for line in out.splitlines():
        pid, ppid, *args = line.split(None, 2)
        rows.append((int(pid), int(ppid), args[0] if args else ""))
    return rows


def started(ctx, pid: int) -> datetime:
    text = process_output(ctx, "ps", "-o", "lstart=", "-p", str(pid)).strip()
    return datetime.strptime(text, "%a %b %d %H:%M:%S %Y").astimezone()


def lock_holder(state: Path, name: str = "chupa.lock") -> datetime | None:
    """When the live lock holder (drain, serve, run, review, ...) started; None when no live process holds the lock.

    A killed drain leaves its lockfile behind, so a pid that no longer exists holds nothing.
    """
    try:
        lock = json.loads((state / name).read_text())
    except OSError, ValueError:
        return None
    if not lock.get("pid") or not lock.get("started_at"):
        return None
    try:
        os.kill(lock["pid"], 0)
    except ProcessLookupError:
        return None
    except PermissionError:
        pass
    return datetime.fromisoformat(lock["started_at"])


def lock_verb(holder: dict, name: str) -> str:
    if holder.get("verb"):
        return holder["verb"]
    if name == "chupa.lock":
        return "chupa"
    try:
        argv = Path(f"/proc/{holder['pid']}/cmdline").read_bytes().decode().split("\0")
        index = argv.index("chupa") + 1
        if argv[index : index + 1] == ["--config"]:
            index += 2
        return argv[index] or "chupa"
    except OSError, ValueError, IndexError, KeyError, UnicodeError:
        return "chupa"


def lock_display(state: Path, name: str) -> tuple[str, str]:
    if lock_holder(state, name) is None:
        return "", ""
    try:
        holder = json.loads((state / name).read_text())
        verb = lock_verb(holder, name)
        return f"{verb} since {clock(holder['started_at'])} (pid {holder['pid']})", verb
    except OSError, ValueError, KeyError:
        return "", ""


def running_stems(state: Path, last_state: dict[str, dict]) -> list[str]:
    """Stems journaled `running` by the live lock holder.

    The journal's last `running` outlives a killed engine, and a later holder such as `review` does not reconcile it,
    so a `running` journaled before the holder started is stale.
    """
    since = lock_holder(state)
    if since is None:
        return []
    return [s for s, b in last_state.items() if b.get("to") == "running" and datetime.fromisoformat(b["ts"]) >= since]


def this_repo(ctx, pid: int, config: str | None) -> bool:
    """Whether a drain runs against this checkout: its --config is ours, or it has none and runs here."""
    try:
        cwd = Path(os.readlink(f"/proc/{pid}/cwd"))
    except OSError:
        return False
    return (cwd / config).resolve() == ctx.config if config else cwd.resolve() == ctx.root and ctx.config == ctx.root / "config.yaml"


def drain_processes(ctx, rows: list[tuple[int, int, str]]) -> list[int]:
    """This repo's engine drain processes, oldest first; a self-upgrade re-exec leaves its parent waiting on the child.

    Another host's drain also runs `python -m chupa --config <its config> drain` from this venv.
    """
    pids = []
    for pid, _, args in rows:
        match = re.match(r"\S*python3? -m chupa (?:--config (\S+) )?drain\b", args)
        if match and this_repo(ctx, pid, match.group(1)):
            pids.append(pid)
    return sorted(pids, key=lambda pid: started(ctx, pid))


def live_call(rows: list[tuple[int, int, str]], root: int) -> str:
    """The model call running under the newest drain, read from the provider CLI's command line."""
    children: dict[int, list[int]] = {}
    for pid, ppid, _ in rows:
        children.setdefault(ppid, []).append(pid)
    args = {pid: a for pid, _, a in rows}
    stack, seen = [root], []
    while stack:
        pid = stack.pop()
        seen.append(pid)
        stack.extend(children.get(pid, []))
    for pid in seen:
        argv = args[pid].split()
        if not argv:
            continue
        name = Path(argv[0]).name
        if name == "codex" and "exec" in argv:
            model = argv[argv.index("-m") + 1] if "-m" in argv else "?"
            effort = next((a.split("=", 1)[1] for a in argv if a.startswith("model_reasoning_effort=")), "?")
            return f"codex {model} (reasoning effort {effort})"
        if name == "claude" and "-p" in argv:
            model = argv[argv.index("--model") + 1] if "--model" in argv else "?"
            return f"claude {model}"
        if name == "node" and len(argv) > 1 and argv[1].endswith("@qwen-code/qwen-code/cli-entry.js"):
            model = argv[argv.index("-m") + 1] if "-m" in argv and argv.index("-m") + 1 < len(argv) else "?"
            return f"qwen {model}"
    return ""


def frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text()
    except OSError:
        return {}
    head = text.split("---", 2)[1] if text.startswith("---") else ""
    return dict(re.findall(r"^(\w+):\s*\"?([^\"\n]+)\"?\s*$", head, re.M))


def capability(ctx, events: list[dict], stem: str, surface: str) -> str:
    """Tier/effort chupa asked for: Implement uses the ticket (or its escalation rung); other steps use their spec."""
    if surface != "implement":
        meta = frontmatter(Path(__file__).parent / "specs" / f"{surface}.md")
        return f"{meta.get('tier', '?')}/{meta.get('effort', '?')}" if meta else ""
    window = events
    for i, e in enumerate(events):
        body = e.get("body", {})
        if e.get("ticket") == stem and body.get("signal") == "reject_verdict" and body.get("verdict") == "keep" and body.get("actor") == "operator":
            window = events[i + 1 :]
    rung = next((e["body"]["rung"] for e in reversed(window) if e.get("type") == "cap_consumed" and e.get("ticket") == stem and e["body"].get("cap") == "retry" and "rung" in e["body"]), None)
    if rung:
        return f"{rung['tier']}/{rung['effort']} (escalated)"
    meta = frontmatter(ctx.root / "tickets" / stem / "ticket.md")
    return f"{meta.get('agent_tier', 'medium')}/{meta.get('agent_effort', 'medium')}"


def read_lines(path: Path, limit: int) -> list[dict]:
    rows = []
    for line in path.read_text(errors="replace").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    return rows


def journal(state: Path) -> list[dict]:
    events: list[dict] = []
    for segment in sorted((state / "journal").glob("*.jsonl")):
        for line in segment.read_text(errors="replace").splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
    return events


def current_step(log: list[dict], stem: str) -> tuple[str, str, str | None]:
    """The step `stem` is on, inferred from its last engine-log stage event; when it began; its model surface."""
    stages = [e for e in log if e.get("stem") == stem and e.get("event") in ("stage_start", "stage_end")]
    if not stages:
        return "Starting", "", None
    last = stages[-1]
    name = STEP_NAMES.get(last.get("surface"), last.get("surface", "?"))
    if last["event"] == "stage_start":
        return name, last["ts"], None if last.get("surface") in ("check", "merge") else last.get("surface")
    after = {"requisition_review": "Implement", "implement": "Check", "check": "Review", "review": "Merge", "diagnose": "Retry or hold"}.get(last.get("surface"))
    return (after or f"after {name}"), last["ts"], None


def depends(path: Path) -> list[str]:
    text = path.read_text()
    section = text.split("## Depends on", 1)[1].split("\n## ", 1)[0] if "## Depends on" in text else ""
    return re.findall(r"^- (\S+)", section, re.M)


def held(history, blobs) -> set[str]:
    """Content parks matching a committed ticket."""
    stems = {e.ticket for e in history if e.ticket is not None}
    return {s for s in stems if (blob := parked_blob(history, s)) is not None and blob == blobs.get(s)}


def operator_holds(ctx, history) -> set[str]:
    stems = {e.ticket for e in history if e.ticket is not None}
    if not stems:
        return set()
    caps_config = load_config(ctx.config, cwd=ctx.root).caps
    return {s for s in stems if awaiting_operator(history, s, caps_config)}


def queue(ctx, events: list[dict], last_state: dict[str, dict], running: set[str], held_stems: set[str]) -> list[tuple[str, str, str]]:
    """Every confirmed ticket not yet settled, rejected, or running: (priority, stem, why it is waiting)."""
    done = SETTLED | {"rejected"}
    history = [SimpleNamespace(type=e.get("type"), body=e.get("body", {}), ticket=e.get("ticket"), ts=e.get("ts")) for e in events]
    waiting_on_person = operator_holds(ctx, history)
    held_stems = held_stems | waiting_on_person
    # A dependency is met when it, or every leaf of the split that superseded it, settled: the drain's own test.
    settled = settled_dependencies(SimpleNamespace(type=e.get("type"), body=e.get("body", {}), ticket=e.get("ticket"), ts=e.get("ts")) for e in events)
    rows = []
    for path in sorted((ctx.root / "tickets").glob("*/ticket.md")):
        stem, meta = path.parent.name, frontmatter(path)
        last = last_state.get(stem, {}).get("to")
        if meta.get("state") != "confirmed" or last in done or stem in running:
            continue
        open_deps = [d for d in depends(path) if d not in settled]
        if stem in waiting_on_person:
            spent = next((e["body"].get("mechanical") for e in reversed(events) if e.get("ticket") == stem and e.get("body", {}).get("signal") == "diagnosis"), None)
            why = f"NEEDS YOUR KEEP OR KILL ({spent})" if spent and "cap spent" in spent else "NEEDS YOUR KEEP OR KILL"
        elif stem in held_stems:
            why = "held until the ticket changes"
        elif last == "running":
            why = "interrupted: the engine stopped mid-run; reruns when it restarts"
        elif open_deps:
            why = "waits on " + ", ".join(open_deps)
        elif last is None:
            why = "ready, not run yet"
        else:
            why = f"retry pending (last: {last})"
        rows.append((meta.get("priority", "P2"), stem, why))
    rows.sort()
    try:
        view = json.loads((ctx.state / "queue.json").read_text())
    except FileNotFoundError:
        return rows
    by_stem = {row[1]: row for row in rows}
    ordered = []
    for stem in view["order"]:
        if stem in by_stem and not (by_stem[stem][2].startswith("waits on ") or stem in held_stems):
            priority, _, why = by_stem.pop(stem)
            hints = view["runs_before"].get(stem, [])
            if hints:
                why += "; runs before: " + ", ".join(hints)
            ordered.append((priority, stem, why))
    return ordered + [row for row in rows if row[1] in by_stem]


def recent_steps(state: Path, log: list[dict], limit: int) -> list[dict]:
    """Merge stage and engine lifetime events, newest first."""
    rows = []
    lifecycle = [e for e in log if e.get("event") in ("engine_start", "engine_stop")]
    for e in log:
        event = e.get("event")
        if event in ("stage_start", "stage_end"):
            verb = "start" if event == "stage_start" else f"end ({e.get('outcome', '?')})"
            surface = e.get("surface")
            prefix = surface if surface in STEP_NAMES else "stage"
            suffix = "start" if event == "stage_start" else "ok" if e.get("outcome") == "ok" else "failed"
            name = STEP_NAMES.get(surface, surface)
            if surface == "triage" and "run_seq" in e:
                name = f"{name} #{e['run_seq']}"
            rows.append({"ts": e["ts"], "stem": e.get("stem"), "surface": surface, "attempt": e.get("attempt"), "run_seq": e.get("run_seq"), "text": f"{name} {verb}", "kind": f"{prefix}_{suffix}"})
        elif event in ("phase_start", "phase_end"):
            name = PHASE_NAMES[e["phase"]]
            outcome = e.get("outcome", "?")
            verb = "start" if event == "phase_start" else f"end ({outcome.replace('_', ' ')})"
            suffix = "start" if event == "phase_start" else "failed" if outcome == "failed" else "ok"
            kind = f"{e['phase']}_{suffix}"
            rows.append({"ts": e["ts"], "stem": None, "text": f"{name} {verb}", "kind": kind})
        elif event == "engine_start":
            rows.append({"ts": e["ts"], "stem": None, "text": f"{e['verb']} started (pid {e['pid']})", "kind": "engine_start"})
        elif event == "engine_stop":
            rows.append({"ts": e["ts"], "stem": None, "text": f"{e['verb']} stopped ({e['outcome']})", "kind": "engine_stop"})
    if lifecycle:
        latest = max(enumerate(lifecycle), key=lambda pair: (pair[1]["ts"], pair[0]))[1]
        try:
            holder_pid = json.loads((state / "chupa.lock").read_text()).get("pid") if lock_holder(state) is not None else None
        except OSError, ValueError:
            holder_pid = None
        if latest["event"] == "engine_start" and holder_pid != latest["pid"]:
            rows.append({"ts": latest["ts"], "stem": None, "text": f"{latest['verb']} ended without a stop record (killed?)", "kind": "engine_lost"})
    return sorted(rows, key=lambda row: row["ts"], reverse=True)[:limit]


def text_snapshot(ctx) -> str:
    state = ctx.state
    events = journal(state)
    log = read_lines(state / "engine.log", 4000) if (state / "engine.log").exists() else []
    rows = processes(ctx)
    drains = drain_processes(ctx, rows)
    lines = [f"chupa watch  {datetime.now().astimezone().strftime('%-I:%M:%S %p')}", ""]
    if not drains:
        lines.append("Drain: not running")
        since = None
    else:
        since = started(ctx, drains[0])
        restarts = f", restarted {len(drains) - 1}x on new engine code" if len(drains) > 1 else ""
        lines.append(f"Drain: running since {since.strftime('%-I:%M %p')} (pid {drains[-1]}{restarts})")
    last_state: dict[str, dict] = {}
    for e in events:
        if e.get("type") == "state_transition" and e.get("ticket"):
            last_state[e["ticket"]] = {**e["body"], "ts": e["ts"]}
    running = running_stems(state, last_state)
    lines.append("")
    if running:
        for stem in running:
            attempt = sum(1 for e in events if e.get("type") == "state_transition" and e.get("ticket") == stem and e["body"].get("to") not in ("running", None))
            step, began, surface = current_step(log, stem)
            when = f" for {ago(began)} (since {clock(began)})" if began else ""
            lines.append(f"Now: {stem}  attempt {attempt + 1}  step: {step}{when}")
            if surface:
                lines.append(f"     asked for tier/effort {capability(ctx, events, stem, surface)}")
                model = live_call(rows, drains[-1]) if drains else ""
                lines.append(f"     model: {model or 'no model call running'}")
            else:
                lines.append("     no model call (mechanical step)")
    else:
        lines.append("Now: nothing running")
    if since is not None:
        done = [(s, b) for s, b in last_state.items() if b.get("to") != "running" and local(b["ts"]) >= since]
        lines.append("")
        lines.append("This drain:")
        for stem, body in sorted(done, key=lambda item: item[1]["ts"]):
            outcome = "merged" if body["to"] in SETTLED else f"stopped: {body['to']}"
            if body.get("routed") == "reject_queue":
                outcome += " (held for you)"
            lines.append(f"  {clock(body['ts'])}  {stem}  {outcome}")
        if not done:
            lines.append("  (nothing finished yet)")
    history = [SimpleNamespace(type=e.get("type"), body=e.get("body", {}), ticket=e.get("ticket"), ts=e.get("ts")) for e in events]
    pending = queue(ctx, events, last_state, set(running), held(history, committed_ticket_shas(ctx)))
    lines += ["", f"Queue ({len(pending)} to do):"]
    lines += [f"  {priority}  {stem}  {why}" for priority, stem, why in pending] or ["  (empty)"]
    recent = recent_steps(state, log, 8)
    if recent:
        lines += ["", "Recent steps:"]
        for row in recent:
            stem = f"{row['stem']}  " if row["stem"] is not None else ""
            lines.append(f"  {clock(row['ts'])}  {stem}{row['text']}")
    return "\n".join(lines)


# Recent Steps keeps more history than watch's 8 because its view scrolls.
STEPS = 40


def load_tickets(ctx, skip: set[str]) -> tuple[dict, dict]:
    """Full engine parse of unsettled tickets only."""
    parsed, invalid = {}, {}
    for path in sorted((ctx.root / "tickets").glob("*/ticket.md")):
        stem = path.parent.name
        if stem in skip:
            continue
        try:
            parsed[stem] = parse_ticket(stem, path.read_text(), ctx.root)
        except TicketInvalid as e:
            invalid[stem] = str(e).splitlines()[0] if str(e) else "invalid ticket"
    return parsed, invalid


def simulate(candidates: dict, done: set[str], authored: dict, *, strict: bool) -> list:
    """Pick tickets one at a time the way the drain does; strict stops when nothing is eligible."""
    order, done, remaining = [], set(done), dict(candidates)
    while remaining:
        if strict:
            eligible = [t for t in remaining.values() if set(t.depends) <= done]
        else:
            # Unblocked view: a dependency outside the blocked set (rejected, missing) no longer holds anything back.
            eligible = [t for t in remaining.values() if all(d in done or d not in remaining for d in t.depends)]
        if not eligible:
            if strict:
                break
            eligible = list(remaining.values())  # a depends cycle among blocked tickets: still list them
        pick = order_tickets(eligible, authored)[0]
        order.append(pick)
        done.add(pick.stem)
        del remaining[pick.stem]
    return order


def uncommitted_tickets(ctx) -> tuple[set[str], set[str]]:
    """(stems whose ticket.md differs from HEAD or is untracked, stems never committed): not yet on the ticket plane."""
    out = asyncio.run(ctx.git.status_porcelain(ctx.root, "--", "tickets"))
    dirty, new = set(), set()
    for line in out.splitlines():
        code, path = line[:2], line[3:]
        # `tickets/<stem>/ticket.md` changed, or the whole `tickets/<stem>/` dir is untracked.
        if path.endswith("/ticket.md") or (path.endswith("/") and len(Path(path).parts) == 2):
            dirty.add(Path(path).parts[1])
            if code == "??":
                new.add(Path(path).parts[1])
    return dirty, new


def committed_ticket_shas(ctx) -> dict[str, str]:
    """Each stem's committed ticket.md blob: the content a `requisition_verdict` approves by `ticket_sha`."""
    out = git_output(ctx, "ls-tree", "-r", "HEAD", "--", "tickets")
    shas = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        if path.endswith("/ticket.md"):
            shas[Path(path).parts[1]] = meta.split()[2]
    return shas


def commits(ctx) -> dict[str, dict]:
    out = git_output(ctx, "log", "--format=%H%x1f%h%x1f%an%x1f%aI%x1f%s", "main")
    rows = {}
    for line in out.splitlines():
        sha, short, author, date, subject = line.split("\x1f", 4)
        rows[sha] = {"sha": sha, "short": short, "author": author, "date": date, "subject": subject}
    return rows


def snapshot(ctx) -> dict:
    state = ctx.state
    now = datetime.now().astimezone()
    events = journal(state)
    log = read_lines(state / "engine.log", 4000) if (state / "engine.log").exists() else []
    last: dict[str, dict] = {}
    for e in events:
        if e.get("type") == "state_transition" and e.get("ticket"):
            last[e["ticket"]] = {**e["body"], "ts": e["ts"]}
    tickets, invalid = load_tickets(ctx, {s for s, b in last.items() if b.get("to") in SETTLED | RETIRED})
    history = [SimpleNamespace(type=e.get("type"), body=e.get("body", {}), ticket=e.get("ticket"), ts=e.get("ts"), key=e.get("key")) for e in events]
    from chupa.reconcile import orphans

    authored = authored_at(history)
    # The drain's own test: a dependency is met when it, or every leaf of the split that superseded it, settled.
    settled = set(settled_dependencies(history))
    blobs = committed_ticket_shas(ctx)
    reject_stems = operator_holds(ctx, history)
    held_stems = held(history, blobs) | reject_stems

    def to(stem: str) -> str | None:
        return last.get(stem, {}).get("to")

    merged = sorted((s for s in last if to(s) in SETTLED), key=lambda s: last[s]["ts"], reverse=True)
    alive = lock_holder(state) is not None
    interrupted = set(orphans(history)) if not alive else set()
    lock, verb = lock_display(state, "chupa.lock")
    commit_lock, _ = lock_display(state, "commit.lock")
    running = running_stems(state, last)
    open_ = {s: t for s, t in tickets.items() if to(s) not in SETTLED | RETIRED and s not in running and t.frontmatter.state not in ("rejected", "merged")}
    runnable = {s: t for s, t in open_.items() if t.frontmatter.state == "confirmed" and s not in held_stems}
    queued = simulate(runnable, settled | set(running), authored, strict=True)
    queued_stems = {t.stem for t in queued}
    blocked = simulate({s: t for s, t in open_.items() if s not in queued_stems}, settled | set(running) | queued_stems, authored, strict=False)
    blocked_stems = {t.stem for t in blocked}

    dirty, new = uncommitted_tickets(ctx)
    verdicts: dict[str, dict[str, str]] = {}  # stem -> ticket_sha -> last verdict for that content
    for e in events:
        body = e.get("body", {})
        if e.get("type") == "signal" and body.get("signal") == "requisition_verdict" and e.get("ticket"):
            verdicts.setdefault(e["ticket"], {})[body.get("ticket_sha")] = body.get("verdict")

    def review(stem: str) -> str:
        """The buildability review for the ticket's current committed text; the drain reviews before a first run."""
        if stem in new or stem not in blobs:
            return "not reviewed: reviewed before its first run, once committed"
        verdict = verdicts.get(stem, {}).get(blobs[stem])
        if verdict == "approve":
            return "approved"
        if verdict:
            return f"{verdict} on this text: edit the ticket to address the findings"
        if verdicts.get(stem):
            return "approved an earlier version: re-reviewed before it runs"
        return "not reviewed: reviewed before its first run"

    def why_blocked(t) -> str:
        if t.stem in new:
            return "new: confirmed by next intake"  # human intake auto-confirms a new hand-written ticket
        if t.frontmatter.state != "confirmed":
            return t.frontmatter.state
        if t.stem in held_stems and t.stem not in reject_stems:
            return f"held until the ticket changes (last: {to(t.stem)})"
        if t.stem in reject_stems:
            spent = next((e["body"].get("mechanical") for e in reversed(events) if e.get("ticket") == t.stem and e.get("body", {}).get("signal") == "diagnosis"), None)
            return f"held: {spent}" if spent else f"held (last: {to(t.stem)})"
        waits = [d for d in t.depends if d not in settled]
        return "waits on " + ", ".join(waits) if waits else "not eligible"

    def why_queued(t) -> str:
        if to(t.stem) == "running":
            return "interrupted: the engine stopped mid-run; reruns when it restarts"
        if to(t.stem) is not None:
            return f"retry pending (last: {to(t.stem)})"
        waits = [d for d in t.depends if d not in settled]
        return "after " + ", ".join(waits) if waits else "ready"

    def base(stem: str, section: str, status: str) -> dict:
        t, path = tickets.get(stem), ctx.root / "tickets" / stem / "ticket.md"
        return {
            "stem": stem,
            "section": section,
            "status": status,
            "priority": t.frontmatter.priority if t else frontmatter(path).get("priority", ""),
            "depends": list(t.depends) if t else depends(path) if path.exists() else [],
            "goal": t.sections.get("Goal / Why", "") if t else "",
            "runsBefore": list(t.runs_before) if t else [],
            "path": f"tickets/{stem}/ticket.md",
            "held": stem in held_stems,
            # Only a committed draft awaits `chupa confirm`; intake confirms a new hand-written one itself.
            "draft": bool(t) and t.frontmatter.state == "draft" and stem not in new,
            # Pending ticket changes go through intake before a verdict is submitted.
            "committed": stem not in dirty,
            # What `chupa run` accepts: confirmed, every dependency settled (it also needs the lock).
            "runnable": bool(t) and t.frontmatter.state == "confirmed" and set(t.depends) <= settled,
            "review": review(stem) if section != "merged" else "",
        }

    # Invalid rows lead the blocked section: they usually depend on valid ones, and graph edges only point down.
    rows = [{**base(stem, "blocked", "invalid: " + why), "goal": ""} for stem, why in sorted(invalid.items()) if to(stem) not in SETTLED | RETIRED and stem not in running]
    rows += [base(t.stem, "blocked", why_blocked(t)) for t in reversed(blocked)]
    rows += [base(t.stem, "queued", why_queued(t)) for t in reversed(queued)]
    for stem in running:
        step, began, _ = current_step(log, stem)
        rows.append(base(stem, "running", f"running: {step}" + (f" for {ago(began)}" if began else "")))
    log_rows = commits(ctx)
    for stem in merged:
        body = last[stem]
        row = base(stem, "merged", "merged" if body["to"] == "merged" else body["to"].replace("_", " "))
        row["commit"] = log_rows.get(body.get("commit", ""))
        row["mergedAt"] = body["ts"]
        row["mergedAtAgo"] = relative(body["ts"], now)
        row["mergedAtDisplay"] = local(body["ts"]).strftime("%x, %X")
        if row["commit"]:
            row["commit"] = {**row["commit"], "dateAgo": relative(row["commit"]["date"], now), "dateDisplay": local(row["commit"]["date"]).strftime("%x, %X")}
        rows.append(row)
    shown = {r["stem"] for r in rows}
    unmerged = [r["stem"] for r in rows if r["section"] != "merged"]
    priorities = list(get_args(Frontmatter.model_fields["priority"].annotation))

    def available(possible: bool) -> str:
        return "locked" if possible and alive else "on" if possible else "off"

    for r in rows:
        open_section = r["section"] in ("queued", "blocked")
        valid = r["stem"] not in invalid
        draft = bool(tickets.get(r["stem"])) and tickets[r["stem"]].frontmatter.state == "draft"
        r["menu"] = {
            "chupaReview": "on" if open_section and valid else "off",
            "chupaLint": "on" if r["section"] != "merged" else "off",
            "chupaRun": available(r["runnable"]),
            "chupaConfirm": "on" if verdict_refusal(history, r["stem"], False, draft, interrupted) is None else "off",
            "chupaReject": "on" if verdict_refusal(history, r["stem"], True, draft, interrupted) is None else "off",
            "chupaAskDiagnose": "on" if r["section"] != "merged" else "off",
            "chupaAskReview": "on" if open_section else "off",
            "chupaPriority": "on" if open_section and valid else "off",
            "chupaRunsBefore": "on" if open_section and valid else "off",
        }
        r["priorityChoices"] = [{"label": p, "description": "current" if p == r["priority"] else ""} for p in priorities]
        r["priorityTag"] = r["priority"] if r["section"] in ("running", "queued") else ""
        if r["section"] != "merged":
            r["runsBeforeChoices"] = [{"label": stem, "picked": stem in r["runsBefore"]} for stem in unmerged if stem != r["stem"]]
        r["depends"] = [d for d in r["depends"] if d in shown]
        detail = [{"heading": None, "text": r["status"] + (f" · {r['priority']}" if r["priority"] else "")}]
        if r["review"]:
            detail.append({"heading": None, "text": f"review: {r['review']}"})
        if r["section"] == "merged":
            if c := r["commit"]:
                detail.append({"heading": "Commit", "text": c["subject"]})
                detail.append({"heading": None, "text": f"{c['short']} · {c['author']} · {c['dateAgo']} ({c['dateDisplay']})"})
            else:
                detail.append({"heading": None, "text": "no commit on main"})
            if r["mergedAt"]:
                detail.append({"heading": None, "text": f"settled {r['mergedAtAgo']} ({r['mergedAtDisplay']})"})
        else:
            detail.extend(
                [
                    {"heading": "Goal / Why", "text": r["goal"] or "(none)"},
                    {"heading": "Runs before", "text": ", ".join(r["runsBefore"]) or "(none)"},
                ]
            )
        if r["depends"]:
            detail.append({"heading": "Depends on", "text": ", ".join(r["depends"])})
        r["detail"] = detail
    for row, graph in zip(rows, layout(rows)):
        row["graph"] = graph
    from chupa.box import Box
    from chupa.seams import LocalFileSystem
    from chupa.status import project

    box = Box(state / "box", LocalFileSystem())
    messages = box.messages()
    labels = {id: (cls, label, summary) for id, cls, label, summary in project([], box=box).box}
    box_rows = []
    for m in reversed(messages):
        cls, label, summary = labels[m.id]
        fields = [["Summary", m.summary], ["Origin", m.origin]]
        if m.stage is not None:
            fields.append(["Stage", f"{m.stage}: {m.outcome}"])
        if m.reports:
            fields.append(["Re-reports", str(m.reports)])
        if m.verdict:
            fields.append(["Recorded verdict", f"{m.verdict.verdict}: {m.verdict.rationale}"])
        if m.resolution:
            fields.append(["Resolution", f"{m.resolution.kind} -> {m.resolution.link}"])
        for title, value in (("Fixed failure", m.fixed_failure), ("Overcorrection risk", m.overcorrection_risk), ("Retro report", m.retro_report_key)):
            if value:
                fields.append([title, value])
        if m.proposed_spec_paths:
            fields.append(["Proposed specs", "\n".join(m.proposed_spec_paths)])
        if m.test_issue:
            fields.append(["Test issue", m.test_issue])
        if m.proposed_paths:
            fields.append(["Proposed paths", "\n".join(m.proposed_paths)])
        path = box.path(m).resolve()
        link = None
        if m.resolution:
            link = str(Path("tickets") / m.resolution.link / "ticket.md") if m.resolution.kind == "ticket" else str(Path("tickets/decisions") / (m.resolution.link + ".md"))
        box_rows.append(
            {
                "id": m.id,
                "seq": m.seq,
                "messageClass": cls,
                "state": m.status,
                "menu": {"chupaTriage": available(m.status == "pending"), "chupaDismiss": available(m.status == "pending")},
                "status": f"{cls} · {label}",
                "summary": summary,
                "fields": fields,
                "path": str(path.relative_to(ctx.root.resolve())) if path.is_relative_to(ctx.root.resolve()) else None,
                "link": link,
            }
        )
    steps = recent_steps(state, log, STEPS)
    for step in steps:
        surface = step.pop("surface", None)
        attempt = step.pop("attempt", None)
        run_seq = step.pop("run_seq", None)
        if surface in ("author", "triage"):
            # Author keys its box message by attempt; triage by run_seq (its attempt is the pass number).
            seq = attempt if surface == "author" else run_seq
            message = next((row for row in box_rows if row["seq"] == seq), None)
            link = message["link"] if message and not step["kind"].endswith("_start") else None
            step["path"] = link if link and (ctx.root / link).is_file() else message["path"] if message else None
        elif surface == "retro":
            path = f"tickets/retro/{run_seq:06d}.md" if run_seq is not None else None
            step["path"] = path if path and (ctx.root / path).is_file() else None
        elif stem := step.get("stem"):
            name = {"implement": "run.md", "check": "checks.json", "review": "review.md", "diagnose": "diagnosis.json"}.get(surface, "ticket.md")
            path = Path("tickets") / stem / name
            fallback = path.with_name("ticket.md")
            step["path"] = str(path) if (ctx.root / path).is_file() else str(fallback) if (ctx.root / fallback).is_file() else None
        step["timeDisplay"] = clock(step["ts"])
        step["dateDisplay"] = local(step["ts"]).strftime("%x, %X")
    box_counts = {
        kind: sum(m.status == "pending" if kind == "pending" else m.resolution is not None and m.resolution.kind == ("ticket" if kind == "author" else kind) for m in messages)
        for kind in ("pending", "author", "tombstone", "declined")
    }
    counts = {section: sum(r["section"] == section for r in rows) for section in ("blocked", "queued", "running", "merged")}
    total = counts["queued"] + counts["running" if alive else "blocked"]
    tooltip = f"{counts['running']} running, {counts['queued']} queued" if alive else f"engine stopped: {counts['blocked']} blocked, {counts['queued']} queued"
    badge = {"value": total, "tooltip": tooltip} if total else None
    return {
        "badge": badge,
        "box": box_rows,
        "boxCounts": box_counts,
        "priorities": priorities,
        "watch": [{"base": str(ctx.root.resolve()), "glob": "tickets/*/ticket.md"}, {"base": str(state.resolve()), "glob": "{journal/*.jsonl,queue.json,engine.log,box/*.json}"}],
        "drainCommand": ["drain", "--detach"],
        "engineVerbs": [
            {"label": "Drain", "detail": "Run every eligible ticket to quiescence, then exit.", "argv": ["drain", "--detach"]},
            {"label": "Serve", "detail": "Run the continuous daemon until kill, stop, or a signal.", "argv": ["serve"]},
            {"label": "Stop after the running ticket", "detail": "Finish the running ticket, admit nothing new, then exit.", "argv": ["stop"]},
            {"label": "Kill (drain or serve)", "detail": "Hard-stop the running drain or serve.", "argv": ["kill"]},
            {"label": "Status", "detail": "Print the journal projection.", "argv": ["status"]},
            {"label": "Retro", "detail": "Run a retro report now, or after the running ticket when an engine is running.", "argv": ["retro"]},
        ],
        "counts": counts,
        "runningStem": running[0] if running else None,
        "verdictDecisions": [dict(zip(("request_id", "verb", "stem", "decision", "reason"), row)) for row in project(history).verdict_decisions],
        "verdictCommands": {verb: [verb, "--extension"] for verb in ("confirm", "reject")},
        "stateDir": str(state.resolve()),
        "configPath": str(ctx.config.resolve()),
        "at": now.isoformat(),
        "engine": verb in ENGINE_VERBS,
        "lock": lock,
        "commitLock": commit_lock,
        "rows": rows,
        "steps": steps,
        "blockedCount": len(blocked_stems) + len(invalid),
    }
