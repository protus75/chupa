"""Reproduce journal rereads when completed retro proposals are replayed."""

import asyncio
import json
import os
import sys
import tempfile
import traceback
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


async def check(root):
    from chupa.config import Retro as RetroSettings
    from chupa.git import Git
    from chupa.journal import EventType, Journal
    from chupa.retro import Retro
    from chupa.seams import LocalFileSystem, SubprocessExec

    def clock():
        return datetime(2026, 1, 1, tzinfo=UTC)

    state = root / ".chupa/state"
    journal = Journal(state, clock)
    git = Git(
        SubprocessExec(),
        env=os.environ | {"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com", "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com"},
        timeout=30,
        commit_lock=None,
    )
    await git.init(root, branch="main")
    checkout = SimpleNamespace(repo=root, git=git, journal=journal, fs=LocalFileSystem(), clock=clock, config=SimpleNamespace(state_dir=state, retro=RetroSettings(enabled=False)))
    hook = Retro(checkout, None)
    for sequence in range(1, 4):
        path = root / f"tickets/retro/{sequence:06d}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        proposal = {"fixed_failure": f"failure {sequence}", "overcorrection_risk": "lost coverage", "proposed_spec_paths": ["specs/review.md"]}
        path.write_text("# Retro receipt\n\n```json\n" + json.dumps({"proposals": [proposal]}) + "\n```\n")
        await git._run(root, "add", str(path.relative_to(root)))
        await git._run(root, "commit", "-m", f"report {sequence}")
        commit = await git.rev_parse(root, "HEAD")
        journal.append(EventType.EFFECT_COMPLETION, {"result": {"commit": commit}}, key=f"retro/{sequence}")
        await hook.emit_proposals(f"retro/{sequence}")
    count = 0
    read = journal.read

    def counted():
        nonlocal count
        count += 1
        return read()

    journal.read = counted
    assert await hook(forced=False) is None
    return count <= 3


def main():
    try:
        with tempfile.TemporaryDirectory() as directory:
            passed = asyncio.run(check(Path(directory)))
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2
    print(json.dumps({"regression_result": "pass" if passed else "defect"}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
