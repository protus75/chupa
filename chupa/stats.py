"""Read-only health projection from journal events and committed invoices."""

import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from chupa.journal import EventType

SETTLED = {"merged", "already_satisfied", "rejected"}
SURFACES = {"requisition_review", "implement", "review", "diagnose", "rework", "retro"}


def window_start(events, now, window):
    match = re.fullmatch(r"([1-9][0-9]*)([hdt])", window)
    if not match:
        raise ValueError(f"bad window {window} -- use <N>h, <N>d, or <N>t")
    number, unit = int(match[1]), match[2]
    if unit != "t":
        return now - timedelta(**{"hours" if unit == "h" else "days": number})
    latest = {}
    for event in events:
        if event.type == EventType.STATE_TRANSITION and event.ticket and event.body.get("to") in SETTLED and datetime.fromisoformat(event.ts) <= now:
            latest[event.ticket] = datetime.fromisoformat(event.ts)
    times = sorted(latest.values(), reverse=True)
    return times[number - 1] if len(times) >= number else datetime.fromisoformat(events[0].ts) if events else now


def _summary(values):
    values = sorted(values)
    def percentile(p):
        position = p * (len(values) - 1)
        lower = math.floor(position)
        upper = math.ceil(position)
        return round(values[lower] + (values[upper] - values[lower]) * (position - lower), 1)
    return {"n": len(values), "p50": percentile(.5), "p90": percentile(.9), "max": round(values[-1], 1)}


def project_stats(events, kinds, checks, *, now, window):
    events = [e for e in events if datetime.fromisoformat(e.ts) <= now]
    start = window_start(events, now, window)
    def inside(event):
        return start <= datetime.fromisoformat(event.ts) <= now
    selected = [e for e in events if inside(e)]
    settled = {}
    for e in events:
        if e.type == EventType.STATE_TRANSITION and e.ticket and e.body.get("to") in SETTLED and datetime.fromisoformat(e.ts) <= now:
            settled[e.ticket] = e
    settled = {stem: e for stem, e in settled.items() if inside(e)}
    states = Counter(e.body["to"] for e in settled.values())
    durations, groups, attempts, intake = defaultdict(list), {}, {}, {}
    def sample(name, begin, end):
        if begin is not None and inside(end):
            durations[name].append((datetime.fromisoformat(end.ts) - datetime.fromisoformat(begin.ts)).total_seconds() / 60)
    for e in events:
        if datetime.fromisoformat(e.ts) > now:
            continue
        stem, body = e.ticket, e.body
        if e.type == EventType.SIGNAL and body.get("signal") == "ticket_intake" and stem:
            intake.setdefault(stem, e)
        if e.type == EventType.STATE_TRANSITION and stem:
            state = body.get("to")
            if state == "running":
                attempts[stem] = {"start": e, "implement": None, "review": None, "checked": False}
            else:
                attempt = attempts.pop(stem, None)
                if attempt:
                    sample("attempt", attempt["start"], e)
                    if not attempt["checked"]:
                        sample("check", attempt["implement"], e)
                    if state == "merged" or body.get("stage") == "merge":
                        sample("merge", attempt["review"], e)
                if state == "merged":
                    sample("lead_time", intake.get(stem), e)
        parts = (e.key or "").split("/")
        if len(parts) == 6 and parts[0] == "llm" and parts[3] in SURFACES:
            group = "/".join(parts[:-1])
            data = groups.setdefault(group, {"start": None, "end": None, "surface": parts[3]})
            if e.type == EventType.EFFECT_INTENT and data["start"] is None:
                data["start"] = e
            if e.type == EventType.EFFECT_COMPLETION:
                data["end"] = e
            attempt = attempts.get(stem)
            if attempt and e.type == EventType.EFFECT_COMPLETION and parts[3] in {"implement", "review"}:
                attempt[parts[3]] = e
            if attempt and e.type == EventType.EFFECT_INTENT and parts[3] == "review" and not attempt["checked"]:
                sample("check", attempt["implement"], e)
                attempt["checked"] = True
    for data in groups.values():
        if data["end"]:
            sample(data["surface"], data["start"], data["end"])
    commands = defaultdict(list)
    for e in selected:
        if e.type == EventType.EFFECT_COMPLETION and re.fullmatch(r"ticket-plane/[^/]+/\d+/checks", e.key or "") and e.key in checks:
            for result in checks[e.key].verification:
                if result.seconds is not None:
                    commands[" ".join(result.argv)].append(result.seconds / 60)
    cycles = {}
    for kind in ("feature", "bug", "chore", "unknown", "all"):
        stems = [s for s in settled if kind == "all" or kinds.get(s, "unknown") == kind]
        if not stems and kind != "all":
            continue
        counts = [sum(e.type == EventType.STATE_TRANSITION and e.ticket == s and e.body.get("to") == "running" for e in events) for s in stems]
        snags = sum(e.type == EventType.STATE_TRANSITION and e.ticket in stems and e.body.get("to") == "gate_failed" and e.body.get("stage") == "review" for e in events)
        merged = [counts[i] for i, s in enumerate(stems) if settled[s].body["to"] == "merged"]
        cycles[kind] = {"tickets": len(stems), "attempts_mean": sum(counts) / len(stems) if stems else 0, "attempts_max": max(counts, default=0), "review_snags_mean": snags / len(stems) if stems else 0, "first_pass_yield": sum(n == 1 for n in merged) / len(merged) if merged else None}
    terminals = [e for e in selected if e.type == EventType.STATE_TRANSITION and e.body.get("to") not in {"running", "merged"}]
    escalations = [e for e in selected if e.type == EventType.STATE_TRANSITION and e.body.get("to") != "running" and e.body.get("dispatch") == "escalate"]
    escalated = {e.ticket for e in events if e.type == EventType.STATE_TRANSITION and e.body.get("to") != "running" and e.body.get("dispatch") == "escalate" and datetime.fromisoformat(e.ts) <= now}
    signals = [e.body for e in selected if e.type == EventType.SIGNAL]
    def signal_counts(signal, field):
        return dict(Counter(b[field] for b in signals if b.get("signal") == signal and b.get(field) is not None))
    costs = [e for e in selected if e.type == EventType.EFFECT_COMPLETION and isinstance(e.body.get("cost"), dict)]
    usd = sum(e.body["cost"].get("usd", 0.0) for e in costs)
    surfaces = defaultdict(float)
    for e in costs:
        parts = (e.key or "").split("/")
        if len(parts) == 6 and parts[0] == "llm":
            surfaces[parts[3]] += e.body["cost"].get("usd", 0.0)
    providers = {}
    for b in signals:
        if b.get("signal") == "provider_call_outcome":
            row = providers.setdefault(b["provider"], {"calls": 0, "failures": 0})
            row["calls"] += 1
            row["failures"] += b.get("failure_class") is not None
    return {
        "window": {"spec": window, "start": start.isoformat(), "end": now.isoformat(), "events": len(selected)},
        "throughput": {"intake": sum(b.get("signal") == "ticket_intake" and b.get("new") is True for b in signals), "settled": {s: states[s] for s in ("merged", "already_satisfied", "rejected")}, "merged_per_day": states["merged"] / max(1, (now - start).total_seconds() / 86400)},
        "durations": {name: _summary(values) for name, values in durations.items()},
        "verification": {name: _summary(values) for name, values in sorted(commands.items(), key=lambda item: (-len(item[1]), item[0]))[:10]},
        "cycles": cycles,
        "ladder": {"escalations": len(escalations), "stems": len({e.ticket for e in escalations}), "rungs": dict(Counter(f"{e.body['rung']['tier']}/{e.body['rung']['effort']}" for e in escalations if e.body.get("rung"))), "outcomes": dict(Counter(e.body["to"] for s, e in settled.items() if s in escalated))},
        "failures": {"terminals": dict(Counter(f"{e.body.get('to')}@{e.body.get('stage') or '-'}" for e in terminals)), "reasons": [list(pair) for pair in Counter(e.body["reason"][:80] for e in terminals if e.body.get("reason")).most_common(10)], "dispatch": dict(Counter(e.body["dispatch"] for e in terminals if e.body.get("dispatch"))), "diagnosis": signal_counts("diagnosis", "verdict"), "rework": signal_counts("rework_order", "action"), "requisition": signal_counts("requisition_verdict", "verdict")},
        "holds": {"reject_queue_arrivals": sum(e.body.get("routed") == "reject_queue" for e in terminals), "keeps": dict(Counter(b["actor"] for b in signals if b.get("signal") == "reject_verdict" and b.get("verdict") == "keep" and b.get("actor"))), "abandoned": sum(e.body.get("to") == "abandoned" for e in terminals), "droughts": sum(e.body.get("reason") == "provider_drought" for e in terminals)},
        "spend": {"usd": usd, "usd_per_merge": usd / states["merged"] if states["merged"] else None, "by_surface": dict(surfaces), "tokens": {direction: sum(e.body["cost"].get(f"{direction}_tokens") or 0 for e in costs) for direction in ("input", "output")}, "provider_calls": providers},
    }


def render_stats(stats):
    return "\n\n".join(f"{key}:\n{json.dumps(value, indent=2)}" for key, value in stats.items()) + "\n"
