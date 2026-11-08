#!/usr/bin/env python3
"""The one dev command for this repo. Every task is a subcommand; nothing else is typed.

    ./dev.py                  the full suite
    ./dev.py test [args]      the suite, or the named tests (args go to pytest)
    ./dev.py new STEM [--kind K]  author and lint a feature, bug, or chore ticket
    ./dev.py order STEM [--priority P] [--runs-before [STEM ...]]  reorder a ticket
    ./dev.py review STEM...   review each ticket against merged code
    ./dev.py lint [STEM...]   validate tickets without running or writing anything
    ./dev.py core             refresh the managed conduct block
    ./dev.py covmap           build the coverage map
    ./dev.py triage [ID ...]  triage pending messages
    ./dev.py migrate-box      migrate old box resolutions
    ./dev.py dismiss ID ...   dismiss messages
    ./dev.py suggest SUMMARY  queue an idea for triage
    ./dev.py status           the engine's projected state
    ./dev.py stats [--window W] [--json]  journal health projection
    ./dev.py run STEM         run one ticket through every stage
    ./dev.py serve            run the continuous daemon
    ./dev.py drain            run every eligible ticket to quiescence
    ./dev.py watch [--once]   live view: running ticket, step, model, and the queue
    ./dev.py publish          bump the patch version, build and upload the release
    ./dev.py vscode           package and install the vscode-chupa extension (then reload the window)
    ./dev.py vscode-package   build a VSIX for Marketplace upload
    ./dev.py kill             hard-stop the running drain or serve
    ./dev.py stop             finish the running ticket and exit
    ./dev.py confirm STEM...  keep each named ticket
    ./dev.py reject STEM...   kill each named Reject-queue ticket

Standard library only, so any python3 starts it; every task runs through uv in this repo's environment.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(argv: list[str]) -> None:
    print("$", " ".join(argv), flush=True)
    if subprocess.run(argv, cwd=ROOT, check=False).returncode != 0:
        sys.exit(f"dev: `{' '.join(argv)}` failed")


def chupa(*args: str) -> None:
    run(["uv", "run", "python", "-m", "chupa", *args])


def main() -> None:
    if sys.argv[1:2] == ["test"]:
        run(["uv", "run", "pytest", "-q", *sys.argv[2:]])
        return

    parser = argparse.ArgumentParser(prog="./dev.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="task")
    sub.add_parser("test", help="the suite, or the named tests")
    sub.add_parser("core", help="refresh the managed conduct block")
    sub.add_parser("covmap", help="build the coverage map")
    sub.add_parser("triage", help="triage pending messages").add_argument("ids", nargs="*")
    sub.add_parser("migrate-box", help="migrate old box resolutions")
    sub.add_parser("dismiss", help="dismiss messages").add_argument("ids", nargs="+")
    sub.add_parser("suggest", help="queue an idea for triage").add_argument("summary")
    sub.add_parser("status", help="the engine's projected state")
    stats = sub.add_parser("stats", help="journal health projection")
    stats.add_argument("--window", default="7d")
    stats.add_argument("--json", action="store_true")
    sub.add_parser("lint", help="validate tickets without running them").add_argument("stems", nargs="*")
    new = sub.add_parser("new", help="author and lint a ticket")
    new.add_argument("stem")
    new.add_argument("--kind", choices=("feature", "bug", "chore"), default="feature")
    order = sub.add_parser("order", help="edit a ticket's ordering")
    order.add_argument("stem")
    order.add_argument("--priority", choices=("P0", "P1", "P2", "P3"))
    order.add_argument("--runs-before", nargs="*", metavar="STEM")
    sub.add_parser("run", help="run one ticket through every stage").add_argument("stem")
    sub.add_parser("serve", help="run the continuous daemon")
    sub.add_parser("drain", help="run every eligible ticket to quiescence")
    sub.add_parser("kill", help="hard-stop the running drain or serve")
    sub.add_parser("stop", help="finish the running ticket and exit")
    sub.add_parser("watch", help="live view of the drain and the queue").add_argument("--once", action="store_true")
    sub.add_parser("publish", help="bump the patch version, build and upload the release")
    sub.add_parser("vscode", help="package and install the vscode-chupa extension")
    sub.add_parser("vscode-package", help="build a VSIX for Marketplace upload")
    for verb in ("confirm", "reject", "review"):
        verdict = sub.add_parser(verb, help=f"{verb} each named ticket")
        verdict.add_argument("stems", nargs="+")
        if verb != "review":
            verdict.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    if args.task is None:
        run(["uv", "run", "pytest", "-q"])
    elif args.task == "new":
        chupa("new", args.stem, "--kind", args.kind)
    elif args.task == "order":
        chupa("order", args.stem, *(["--priority", args.priority] if args.priority is not None else []), *(["--runs-before", *args.runs_before] if args.runs_before is not None else []))
    elif args.task == "stats":
        chupa("stats", "--window", args.window, *(["--json"] if args.json else []))
    elif args.task in {"triage", "dismiss"}:
        chupa(args.task, *args.ids)
    elif args.task == "suggest":
        chupa("suggest", args.summary)
    elif args.task == "run":
        chupa("run", args.stem)
    elif args.task == "lint":
        chupa("lint", *args.stems)
    elif args.task == "drain":
        match = re.search(r"^state_dir:\s*(\S+)", (ROOT / "config.yaml").read_text(), re.M)
        state = ROOT / (match.group(1) if match else ".chupa/state")
        state.mkdir(parents=True, exist_ok=True)
        output = state / "drain.out"
        with output.open("a") as stream:
            child = subprocess.Popen(["uv", "run", "python", "-m", "chupa", "drain"], cwd=ROOT, start_new_session=True, stdin=subprocess.DEVNULL, stdout=stream, stderr=stream)
        print(f"dev: drain pid {child.pid}, output {output}")
    elif args.task == "watch":
        try:
            chupa("watch", *(["--once"] if args.once else []))
        except KeyboardInterrupt:
            pass
    elif args.task == "publish":
        if not os.environ.get("UV_PUBLISH_TOKEN"):
            sys.exit("dev: set UV_PUBLISH_TOKEN to publish")
        run(["uv", "version", "--bump", "patch"])
        with tempfile.TemporaryDirectory() as tmp:
            run(["uv", "build", "-o", tmp])
            run(["uv", "publish", *(str(path) for path in sorted(Path(tmp).iterdir()))])
    elif args.task == "vscode-package":
        package = json.loads((ROOT / "vscode-chupa" / "package.json").read_text())
        output = ROOT / "dist" / f"vscode-chupa-{package['version']}.vsix"
        output.parent.mkdir(parents=True, exist_ok=True)
        pack = ["npx", "--yes", "@vscode/vsce", "package", "--no-dependencies", "-o", str(output)]
        print("$", " ".join(pack), flush=True)
        if subprocess.run(pack, cwd=ROOT / "vscode-chupa", check=False).returncode != 0:
            sys.exit("dev: packaging vscode-chupa failed")
        print(f"dev: upload {output} at https://marketplace.visualstudio.com/manage/publishers/chunkydragon")
        if os.environ.get("WSL_DISTRO_NAME"):
            windows_path = subprocess.run(["wslpath", "-w", str(output)], capture_output=True, text=True, check=False)
            if windows_path.returncode != 0:
                sys.exit("dev: wslpath failed")
            print(f"dev: Windows path {windows_path.stdout.strip()}")
    elif args.task == "vscode":
        # VS Code keeps an extension's old icon and views until its version changes, so every install bumps the patch.
        manifest = ROOT / "vscode-chupa" / "package.json"
        package = json.loads(manifest.read_text())
        major, minor, patch = package["version"].split(".")
        package["version"] = f"{major}.{minor}.{int(patch) + 1}"
        manifest.write_text(json.dumps(package, indent="\t") + "\n")
        print(f"dev: vscode-chupa version {package['version']}", flush=True)
        with tempfile.TemporaryDirectory() as tmp:
            vsix = str(Path(tmp) / "vscode-chupa.vsix")
            pack = ["npx", "--yes", "@vscode/vsce", "package", "--allow-missing-repository", "--skip-license", "--no-dependencies", "-o", vsix]
            print("$", " ".join(pack), flush=True)
            if subprocess.run(pack, cwd=ROOT / "vscode-chupa", check=False).returncode != 0:
                sys.exit("dev: packaging vscode-chupa failed")
            run(["code", "--install-extension", vsix, "--force"])
        print("dev: run Developer: Reload Window to load it")
    elif args.task in {"confirm", "reject", "review"}:
        for stem in args.stems:
            chupa(args.task, stem, *(["--yes"] if getattr(args, "yes", False) else []))
    else:
        chupa(args.task)


if __name__ == "__main__":
    main()
