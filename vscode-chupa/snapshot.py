"""One JSON snapshot of every ticket for the vscode-chupa view, top row first. Read-only.

    .venv/bin/python vscode-chupa/snapshot.py

Rows, top to bottom: blocked (in the order they would run if unblocked), the queue (last to run first),
the running ticket, then merged tickets newest first. Each row lists the `Depends on` stems the view
draws as graph parents.
"""

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import watch  # noqa: E402
from chupa.drain import RETIRED, authored_at, order_tickets  # noqa: E402
from chupa.rework import settled_dependencies  # noqa: E402
from chupa.tickets import TicketInvalid, parse_ticket, read_plan  # noqa: E402

SETTLED = watch.SETTLED
# Recent Steps keeps more history than watch's 8 because its view scrolls.
STEPS = 40


def load_tickets(skip: set[str]) -> tuple[dict, dict]:
    """Full engine parse of unsettled tickets only: the plan-cite check makes it cost ~75ms a ticket."""
    plan = read_plan(ROOT)
    parsed, invalid = {}, {}
    for path in sorted((ROOT / "tickets").glob("*/ticket.md")):
        stem = path.parent.name
        if stem in skip:
            continue
        try:
            parsed[stem] = parse_ticket(stem, path.read_text(), ROOT, plan=plan)
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


def uncommitted_tickets() -> tuple[set[str], set[str]]:
    """(stems whose ticket.md differs from HEAD or is untracked, stems never committed): not yet on the ticket plane."""
    out = subprocess.run(["git", "status", "--porcelain", "--", "tickets"], cwd=ROOT, capture_output=True, text=True).stdout
    dirty, new = set(), set()
    for line in out.splitlines():
        code, path = line[:2], line[3:]
        # `tickets/<stem>/ticket.md` changed, or the whole `tickets/<stem>/` dir is untracked.
        if path.endswith("/ticket.md") or (path.endswith("/") and len(Path(path).parts) == 2):
            dirty.add(Path(path).parts[1])
            if code == "??":
                new.add(Path(path).parts[1])
    return dirty, new


def committed_ticket_shas() -> dict[str, str]:
    """Each stem's committed ticket.md blob: the content a `requisition_verdict` approves by `ticket_sha`."""
    out = subprocess.run(["git", "ls-tree", "-r", "HEAD", "--", "tickets"], cwd=ROOT, capture_output=True, text=True).stdout
    shas = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        if path.endswith("/ticket.md"):
            shas[Path(path).parts[1]] = meta.split()[2]
    return shas


def commits() -> dict[str, dict]:
    out = subprocess.run(["git", "log", "--format=%H%x1f%h%x1f%an%x1f%aI%x1f%s", "main"], cwd=ROOT, capture_output=True, text=True).stdout
    rows = {}
    for line in out.splitlines():
        sha, short, author, date, subject = line.split("\x1f", 4)
        rows[sha] = {"sha": sha, "short": short, "author": author, "date": date, "subject": subject}
    return rows


def snapshot() -> dict:
    state = watch.state_dir()
    events = watch.journal(state, limit=10**7)
    log = watch.read_lines(state / "engine.log", 4000)
    last: dict[str, dict] = {}
    for e in events:
        if e.get("type") == "state_transition" and e.get("ticket"):
            last[e["ticket"]] = {**e["body"], "ts": e["ts"]}
    tickets, invalid = load_tickets({s for s, b in last.items() if b.get("to") in SETTLED | RETIRED})
    history = [SimpleNamespace(type=e.get("type"), body=e.get("body", {}), ticket=e.get("ticket"), ts=e.get("ts")) for e in events]
    authored = authored_at(history)
    # The drain's own test: a dependency is met when it, or every leaf of the split that superseded it, settled.
    settled = set(settled_dependencies(history))
    held = watch.held(events)

    def to(stem: str) -> str | None:
        return last.get(stem, {}).get("to")

    merged = sorted((s for s in last if to(s) in SETTLED), key=lambda s: last[s]["ts"], reverse=True)
    alive = watch.lock_holder(state) is not None
    running = watch.running_stems(state, last)
    open_ = {s: t for s, t in tickets.items() if to(s) not in SETTLED | RETIRED and s not in running and t.frontmatter.state not in ("rejected", "merged")}
    runnable = {s: t for s, t in open_.items() if t.frontmatter.state == "confirmed" and s not in held}
    queued = simulate(runnable, settled | set(running), authored, strict=True)
    queued_stems = {t.stem for t in queued}
    blocked = simulate({s: t for s, t in open_.items() if s not in queued_stems}, settled | set(running) | queued_stems, authored, strict=False)
    blocked_stems = {t.stem for t in blocked}

    dirty, new = uncommitted_tickets()
    blobs = committed_ticket_shas()
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
        if t.stem in held:
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
        t, path = tickets.get(stem), ROOT / "tickets" / stem / "ticket.md"
        return {
            "stem": stem,
            "section": section,
            "status": status,
            "priority": t.frontmatter.priority if t else watch.frontmatter(path).get("priority", ""),
            "depends": list(t.depends) if t else watch.depends(path) if path.exists() else [],
            "goal": t.sections.get("Goal / Why", "") if t else "",
            "runsBefore": list(t.runs_before) if t else [],
            "path": f"tickets/{stem}/ticket.md",
            "held": stem in held,
            # Only a committed draft awaits `chupa confirm`; intake confirms a new hand-written one itself.
            "draft": bool(t) and t.frontmatter.state == "draft" and stem not in new,
            # A committed draft can be confirmed while another process holds the lock; an uncommitted one cannot.
            "committed": stem not in dirty,
            # What `chupa run` accepts: confirmed, every dependency settled (it also needs the lock).
            "runnable": bool(t) and t.frontmatter.state == "confirmed" and set(t.depends) <= settled,
            "review": review(stem) if section != "merged" else "",
        }

    rows = [base(t.stem, "blocked", why_blocked(t)) for t in reversed(blocked)]
    rows += [{**base(stem, "blocked", "invalid: " + why), "goal": ""} for stem, why in sorted(invalid.items()) if to(stem) not in SETTLED | RETIRED and stem not in running]
    rows += [base(t.stem, "queued", why_queued(t)) for t in reversed(queued)]
    for stem in running:
        step, began, _ = watch.current_step(log, stem)
        rows.append(base(stem, "running", f"running: {step}" + (f" for {watch.ago(began)}" if began else "")))
    log_rows = commits()
    for stem in merged:
        body = last[stem]
        row = base(stem, "merged", "merged" if body["to"] == "merged" else body["to"].replace("_", " "))
        row["commit"] = log_rows.get(body.get("commit", ""))
        row["mergedAt"] = body["ts"]
        rows.append(row)
    shown = {r["stem"] for r in rows}
    for r in rows:
        r["depends"] = [d for d in r["depends"] if d in shown]
    steps = [
        {
            "ts": e["ts"],
            "stem": e.get("stem"),
            "step": watch.STEP_NAMES.get(e.get("surface"), e.get("surface")),
            "verb": "start" if e["event"] == "stage_start" else f"end ({e.get('outcome', '?')})",
        }
        for e in reversed([e for e in log if e.get("event") in ("stage_start", "stage_end")][-STEPS:])
    ]
    return {
        "at": watch.datetime.now().astimezone().isoformat(),
        "engine": alive,
        "rows": rows,
        "steps": steps,
        "blockedCount": len(blocked_stems) + len(invalid),
    }


if __name__ == "__main__":
    print(json.dumps(snapshot()))
