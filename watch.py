#!/usr/bin/env python3
"""Live view of the running drain: the ticket, its step, and what this drain has done. Read-only.

    python3 watch.py           refresh every 3 seconds until Ctrl-C
    python3 watch.py --once    print one snapshot

Reads the journal and engine log under the config's state_dir; writes nothing and takes no lock.
Standard library only.
"""

import argparse
import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# A stage the engine log records; Check and merge are mechanical and leave no stage events.
STEP_NAMES = {"implement": "Implement", "review": "Review", "diagnose": "Diagnose", "rework": "Rework", "retro": "Retro", "triage": "Triage", "author": "Author"}
SETTLED = {"merged", "already_satisfied"}


def state_dir() -> Path:
    match = re.search(r"^state_dir:\s*(\S+)", (ROOT / "config.yaml").read_text(), re.M)
    return ROOT / (match.group(1) if match else ".chupa/state")


def local(ts: str) -> datetime:
    return datetime.fromisoformat(ts).astimezone()


def clock(ts: str) -> str:
    return local(ts).strftime("%-I:%M %p")


def ago(ts: str) -> str:
    seconds = int((datetime.now().astimezone() - local(ts)).total_seconds())
    return f"{seconds // 60}m{seconds % 60:02d}s"


def processes() -> list[tuple[int, int, str]]:
    out = subprocess.run(["ps", "-eo", "pid=,ppid=,args="], capture_output=True, text=True).stdout
    rows = []
    for line in out.splitlines():
        pid, ppid, *args = line.split(None, 2)
        rows.append((int(pid), int(ppid), args[0] if args else ""))
    return rows


def started(pid: int) -> datetime:
    text = subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
    return datetime.strptime(text, "%a %b %d %H:%M:%S %Y").astimezone()


def drain_processes(rows: list[tuple[int, int, str]]) -> list[int]:
    """Every engine drain process, oldest first; a self-upgrade re-exec leaves its parent waiting on the child."""
    pids = [pid for pid, _, args in rows if re.match(r"\S*python3? -m chupa drain\b", args)]
    return sorted(pids, key=started)


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
    return ""


def frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text()
    except OSError:
        return {}
    head = text.split("---", 2)[1] if text.startswith("---") else ""
    return dict(re.findall(r"^(\w+):\s*\"?([^\"\n]+)\"?\s*$", head, re.M))


def capability(events: list[dict], stem: str, surface: str) -> str:
    """Tier/effort chupa asked for: Implement uses the ticket (or its escalation rung); other steps use their spec."""
    if surface != "implement":
        meta = frontmatter(ROOT / "specs" / f"{surface}.md")
        return f"{meta.get('tier', '?')}/{meta.get('effort', '?')}" if meta else ""
    window = events
    for i, e in enumerate(events):
        body = e.get("body", {})
        if e.get("ticket") == stem and body.get("signal") == "reject_verdict" and body.get("verdict") == "keep" and body.get("actor") == "operator":
            window = events[i + 1 :]
    rung = next((e["body"]["rung"] for e in reversed(window) if e.get("type") == "cap_consumed" and e.get("ticket") == stem and e["body"].get("cap") == "retry" and "rung" in e["body"]), None)
    if rung:
        return f"{rung['tier']}/{rung['effort']} (escalated)"
    meta = frontmatter(ROOT / "tickets" / stem / "ticket.md")
    return f"{meta.get('agent_tier', 'medium')}/{meta.get('agent_effort', 'medium')}"


def read_lines(path: Path, limit: int) -> list[dict]:
    rows = []
    for line in path.read_text(errors="replace").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    return rows


def journal(state: Path, limit: int = 20000) -> list[dict]:
    segments = sorted((state / "journal").glob("*.jsonl"))
    events: list[dict] = []
    for segment in reversed(segments):
        events = read_lines(segment, limit) + events
        if len(events) >= limit:
            break
    return events[-limit:]


def current_step(log: list[dict], stem: str) -> tuple[str, str, str | None]:
    """The step `stem` is on, inferred from its last engine-log stage event; when it began; its model surface."""
    stages = [e for e in log if e.get("stem") == stem and e.get("event") in ("stage_start", "stage_end")]
    if not stages:
        return "Starting", "", None
    last = stages[-1]
    name = STEP_NAMES.get(last.get("surface"), last.get("surface", "?"))
    if last["event"] == "stage_start":
        return name, last["ts"], last.get("surface")
    after = {"implement": "Check", "review": "Merge", "diagnose": "Retry or hold"}.get(last.get("surface"))
    return (after or f"after {name}"), last["ts"], None


def depends(path: Path) -> list[str]:
    text = path.read_text()
    section = text.split("## Depends on", 1)[1].split("\n## ", 1)[0] if "## Depends on" in text else ""
    return re.findall(r"^- (\S+)", section, re.M)


def held(events: list[dict]) -> set[str]:
    """Stems waiting on a person's keep or kill: the same fold `chupa status` uses for its Reject queue."""
    terminals: dict[str, dict] = {}
    waiting: set[str] = set()
    for e in events:
        stem, body = e.get("ticket"), e.get("body", {})
        if stem is None:
            continue
        if e.get("type") == "state_transition" and body.get("to") != "running":
            terminals[stem] = body
            waiting.discard(stem)
            if body.get("routed") == "reject_queue":
                waiting.add(stem)
        elif body.get("signal") == "reject_arrival" and stem in terminals:
            waiting.add(stem)
        elif body.get("signal") == "reject_verdict":
            waiting.discard(stem)
    return {s for s in waiting if terminals[s].get("to") not in SETTLED}


def queue(events: list[dict], last_state: dict[str, dict]) -> list[tuple[str, str, str]]:
    """Every confirmed ticket not yet settled or rejected: (priority, stem, why it is waiting)."""
    done = SETTLED | {"rejected"}
    waiting_on_person = held(events)
    rows = []
    for path in sorted((ROOT / "tickets").glob("*/ticket.md")):
        stem, meta = path.parent.name, frontmatter(path)
        last = last_state.get(stem, {}).get("to")
        if meta.get("state") != "confirmed" or last in done or last == "running":
            continue
        open_deps = [d for d in depends(path) if last_state.get(d, {}).get("to") not in SETTLED]
        if stem in waiting_on_person:
            spent = next((e["body"].get("mechanical") for e in reversed(events) if e.get("ticket") == stem and e.get("body", {}).get("signal") == "diagnosis"), None)
            why = f"NEEDS YOUR KEEP OR KILL ({spent})" if spent and "cap spent" in spent else "held; the drain retries it when new work runs out"
        elif open_deps:
            why = "waits on " + ", ".join(open_deps)
        elif last is None:
            why = "ready, not run yet"
        else:
            why = f"retry pending (last: {last})"
        rows.append((meta.get("priority", "P2"), stem, why))
    return sorted(rows)


def snapshot() -> str:
    state = state_dir()
    events = journal(state)
    log = read_lines(state / "engine.log", 4000)
    rows = processes()
    drains = drain_processes(rows)
    lines = [f"chupa watch  {datetime.now().astimezone().strftime('%-I:%M:%S %p')}", ""]
    if not drains:
        lines.append("Drain: not running")
        since = None
    else:
        since = started(drains[0])
        restarts = f", restarted {len(drains) - 1}x on new engine code" if len(drains) > 1 else ""
        lines.append(f"Drain: running since {since.strftime('%-I:%M %p')} (pid {drains[-1]}{restarts})")
    last_state: dict[str, dict] = {}
    for e in events:
        if e.get("type") == "state_transition" and e.get("ticket"):
            last_state[e["ticket"]] = {**e["body"], "ts": e["ts"]}
    running = [s for s, b in last_state.items() if b.get("to") == "running"]
    lines.append("")
    if running:
        for stem in running:
            attempt = sum(1 for e in events if e.get("type") == "state_transition" and e.get("ticket") == stem and e["body"].get("to") not in ("running", None))
            step, began, surface = current_step(log, stem)
            when = f" for {ago(began)} (since {clock(began)})" if began else ""
            lines.append(f"Now: {stem}  attempt {attempt + 1}  step: {step}{when}")
            if surface:
                lines.append(f"     asked for tier/effort {capability(events, stem, surface)}")
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
    pending = queue(events, last_state)
    lines += ["", f"Queue ({len(pending)} to do):"]
    lines += [f"  {priority}  {stem}  {why}" for priority, stem, why in pending] or ["  (empty)"]
    recent = [e for e in log if e.get("event") in ("stage_start", "stage_end")][-8:]
    if recent:
        lines += ["", "Recent steps:"]
        for e in recent:
            verb = "start" if e["event"] == "stage_start" else f"end ({e.get('outcome', '?')})"
            lines.append(f"  {clock(e['ts'])}  {e.get('stem')}  {STEP_NAMES.get(e.get('surface'), e.get('surface'))} {verb}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--once", action="store_true", help="print one snapshot and exit")
    args = parser.parse_args()
    if args.once:
        print(snapshot())
        return
    try:
        while True:
            print("\033[2J\033[H" + snapshot(), flush=True)
            time.sleep(3)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
