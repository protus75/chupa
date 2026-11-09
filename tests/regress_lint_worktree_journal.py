"""Carried reproducer for lint reading the main journal from a worktree."""

import contextlib
import io
import json
import sys
import tempfile
import traceback
from pathlib import Path


def main() -> int:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from chupa.__main__ import main as chupa_main
        from chupa.journal import EventType
        from tests.integration.test_cli import ENV, Clock, journal, root, ticket, write
        from tests.integration.test_lint_verb import git

        with tempfile.TemporaryDirectory() as directory:
            repo = root.__wrapped__(Path(directory))
            write(repo, "merged", "old invalid grammar\n")
            write(repo, "active", ticket().replace("priority: P2", "state: confirmed\nsource: human\npriority: P2"))
            git(repo, "add", "--", "tickets")
            git(repo, "commit", "-m", "tickets")
            journal(repo).append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="merged")
            worktree = Path(directory) / "worktree"
            git(repo, "worktree", "add", "--detach", str(worktree))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = chupa_main(["lint"], cwd=worktree, env=ENV, clock=Clock())
            text = output.getvalue()
            if result == 0 and text == "lint: 1/1 tickets valid\n":
                outcome, code = "pass", 0
            elif result == 1 and "tickets/merged/ticket.md:" in text:
                outcome, code = "defect", 1
            else:
                raise RuntimeError(f"unexpected lint result {result}: {text!r}")
    except Exception:
        traceback.print_exc(file=sys.stderr)
        outcome, code = "error", 2
    print(json.dumps({"regression_result": outcome}))
    return code


if __name__ == "__main__":
    sys.exit(main())
