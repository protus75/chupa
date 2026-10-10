"""Disposable fixture setup only; no engine lifecycle or report producer."""

import json
import shutil
from pathlib import Path


SOURCE = Path(__file__).resolve().parent
SCENARIOS = ("merge-add", "merge-bonus", "merge-floor", "regression", "escape")
SURFACES = ("author", "implement", "review", "triage")


def copy_host(destination):
    destination = Path(destination).resolve()
    if destination == SOURCE or SOURCE in destination.parents:
        raise ValueError("choose a disposable destination outside the committed fixture")
    shutil.copytree(SOURCE, destination, ignore=shutil.ignore_patterns("__pycache__"))
    runtime = destination / ".fixture-runtime"
    runtime.mkdir()
    (runtime / "root").write_text(str(destination))
    return destination


def require_disposable(root):
    root = Path(root).resolve()
    marker = root / ".fixture-runtime" / "root"
    if not marker.is_file() or marker.read_text() != str(root):
        raise ValueError("runtime writes require a disposable host; use scaffold.copy_host first")
    return root


def scenario(root, name):
    if name not in SCENARIOS:
        raise ValueError(f"unknown script {name!r}; select a declared scenario: {', '.join(SCENARIOS)}")
    return json.loads((Path(root) / "scripts.json").read_text())[name]


def scripted_reply(root, name, surface, prompt, writes, *, workspace=None):
    root = require_disposable(root)
    work = root if workspace is None else Path(workspace).resolve()
    if work != root and work != root / ".chupa/worktrees" / name:
        raise ValueError("select this scenario's disposable worktree")
    row = scenario(root, name)
    if surface not in SURFACES:
        raise ValueError(f"unknown surface; select one of {', '.join(SURFACES)}")
    runtime = root / ".fixture-runtime"
    cursor = runtime / "cursors.json"
    counts = json.loads(cursor.read_text()) if cursor.exists() else {}
    key = f"{name}/{surface}"
    index = counts.get(key, 0)
    replies = row["responses"][surface]
    if index >= len(replies):
        raise ValueError(f"exhausted script {key}; replenish its declared responses in a disposable copy")
    if writes != (surface == "implement"):
        raise ValueError("permission grant disagrees with surface; use the existing Claude adapter")
    if surface == "implement":
        # Closed host edit vocabulary; no arbitrary path or code execution.
        if set(row["edits"]) != ({"settings.json", "fixtures/report_regression.py", "fixtures/replay.json"}
                                 if name == "regression" else {"settings.json"}):
            raise ValueError("undeclared host edit; select the declared settings and regression fixture edits")
        target = work / "settings.json"
        if target.is_symlink() or not target.is_file():
            raise ValueError("settings.json must be a host regular file; restore it in the disposable copy")
        settings = json.loads(target.read_text())
        changes = row["edits"]["settings.json"]
        if not set(changes) <= {"add_scale", "bonus_scale", "floor", "spend_sign"}:
            raise ValueError("unknown setting; use the declared score settings")
        target.write_text(json.dumps({**settings, **changes}, sort_keys=True) + "\n")
        if name == "regression":
            target = work / "fixtures/report_regression.py"
            target.parent.mkdir(exist_ok=True)
            if target.is_symlink() or target.parent.is_symlink():
                raise ValueError("restore a regular fixtures directory in the disposable host")
            target.write_text(row["edits"]["fixtures/report_regression.py"])
            target = work / "fixtures/replay.json"
            if target.is_symlink():
                raise ValueError("restore a regular carried replay in the disposable host")
            target.write_text(row["edits"]["fixtures/replay.json"])
    (runtime / f"{name}-{surface}-{index}.prompt").write_text(prompt)
    counts[key] = index + 1
    cursor.write_text(json.dumps(counts, sort_keys=True))
    return json.dumps(replies[index])
