#!/usr/bin/env python3
"""The one dev command for this repo. Every task is a subcommand; nothing else is typed.

    ./dev.py                  the full suite
    ./dev.py test [args]      the suite, or the named tests (args go to pytest)
    ./dev.py new STEM [--kind K]  author and lint a feature, bug, or chore ticket
    ./dev.py lint [STEM...]   validate tickets without running or writing anything
    ./dev.py status           the engine's projected state
    ./dev.py drain            run every eligible ticket to quiescence
    ./dev.py kill             hard-stop the running drain or serve
    ./dev.py reject STEM...   kill each named Reject-queue ticket

Standard library only, so any python3 starts it; every task runs through uv in this repo's environment.
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(argv: list[str]) -> None:
    print("$", " ".join(argv), flush=True)
    if subprocess.run(argv, cwd=ROOT, check=False).returncode != 0:
        sys.exit(f"dev: `{' '.join(argv)}` failed")


def chupa(*args: str) -> None:
    run(["uv", "run", "python", "-m", "chupa", *args])


def main() -> None:
    parser = argparse.ArgumentParser(prog="./dev.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="task")
    sub.add_parser("test", help="the suite, or the named tests").add_argument("args", nargs=argparse.REMAINDER)
    sub.add_parser("status", help="the engine's projected state")
    sub.add_parser("lint", help="validate tickets without running them").add_argument("stems", nargs="*")
    new = sub.add_parser("new", help="author and lint a ticket")
    new.add_argument("stem")
    new.add_argument("--kind", choices=("feature", "bug", "chore"), default="feature")
    sub.add_parser("drain", help="run every eligible ticket to quiescence")
    sub.add_parser("kill", help="hard-stop the running drain or serve")
    sub.add_parser("reject", help="kill each named Reject-queue ticket").add_argument("stems", nargs="+")
    args = parser.parse_args()
    if args.task is None:
        run(["uv", "run", "pytest", "-q"])
    elif args.task == "test":
        run(["uv", "run", "pytest", "-q", *args.args])
    elif args.task == "new":
        chupa("new", args.stem, "--kind", args.kind)
    elif args.task == "lint":
        chupa("lint", *args.stems)
    elif args.task == "reject":
        for stem in args.stems:
            chupa("reject", stem)
    else:
        chupa(args.task)


if __name__ == "__main__":
    main()
