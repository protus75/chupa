"""Reconcile-on-entry (CHUPA_PLAN.md sections 6, 11, 18): reap orphaned in-flight runs before dispatch.

Called only by a scaffold verb holding the sole writer lock with no daemon alive, so a run still open
in the journal is provably dead. Phase 1 reaps minimally: journal `abandoned`, then wipe the worktree
(section 11.2's journal -> wipe order). Harvest of the orphan folds in with the Phase 2 spine.
"""

from collections.abc import Iterable
from pathlib import Path

from chupa.git import Git
from chupa.journal import TERMINAL_STATES, Event, EventType, Journal


def orphans(events: Iterable[Event]) -> list[str]:
    """Stems whose run is still open: a `running`, or an intent with no completion, since their last terminal."""
    running: set[str] = set()
    intents: dict[str, set[str]] = {}
    for e in events:
        if e.ticket is None:
            continue
        if e.type == EventType.STATE_TRANSITION:
            if e.body.get("to") in TERMINAL_STATES:
                running.discard(e.ticket)
                intents.pop(e.ticket, None)
            elif e.body.get("to") == "running":
                running.add(e.ticket)
        elif e.type == EventType.EFFECT_INTENT:
            intents.setdefault(e.ticket, set()).add(e.key)
        elif e.type == EventType.EFFECT_COMPLETION:
            intents.get(e.ticket, set()).discard(e.key)
    return sorted(running | {stem for stem, keys in intents.items() if keys})


async def reconcile(journal: Journal, git: Git, repo: Path, worktree_root: Path) -> list[str]:
    """Reap every orphan to `abandoned` and remove its worktree; return the reaped stems (empty: a no-op)."""
    reaped = orphans(journal.read())
    for stem in reaped:
        journal.append(EventType.STATE_TRANSITION, {"to": "abandoned"}, ticket=stem)
        # Journal before wipe: a wipe that fails leaves a leftover the next run's teardown-and-create removes.
        path = worktree_root / stem
        if path.exists():
            await git.worktree_remove(repo, path)
    if reaped:
        await git.worktree_prune(repo)
    return reaped
