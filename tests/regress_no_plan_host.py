import contextlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def run():
    from chupa.__main__ import main
    from tests.test_cli import ENV, git_out
    from tests.test_drain import Clock, commit_ticket, confirmed, make_root

    with tempfile.TemporaryDirectory() as directory:
        root = make_root(Path(directory))
        (root / "CHUPA_PLAN.md").unlink()
        git_out(root, "add", "-u", "CHUPA_PLAN.md")
        git_out(root, "commit", "-m", "remove plan")
        commit_ticket(root, "parent", confirmed())
        commit_ticket(root, "child", confirmed(depends="- parent"))
        if main(["reject", "parent"], cwd=root, env=ENV, clock=Clock()) != 0:
            raise RuntimeError("reject failed")
        if not list((root / ".chupa/state/box").glob("*.json")):
            raise RuntimeError("dead dependency report missing")


def main_result():
    try:
        with contextlib.redirect_stdout(sys.stderr):
            run()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return ("defect", 1) if "CHUPA_PLAN.md" in str(exc) else ("error", 2)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return "error", 2
    return "pass", 0


if __name__ == "__main__":
    result, code = main_result()
    print(json.dumps({"regression_result": result}))
    sys.exit(code)
