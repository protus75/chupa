import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from chupa.driver import Driver


def test_stage_event_writers_are_confined_to_driver_stage():
    writers = []
    for path in sorted(Path("chupa").glob("*.py")):
        tree = ast.parse(path.read_text())
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args or not isinstance(node.args[0], ast.Constant) or node.args[0].value not in {"stage_start", "stage_end"}:
                continue
            if not isinstance(node.func, ast.Attribute) or node.func.attr != "event":
                continue
            enclosing = []
            current = node
            while current in parents:
                current = parents[current]
                if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    enclosing.append(current.name)
            writers.append((str(path), enclosing))
    assert len(writers) == 2
    assert all(path == "chupa/driver.py" and "stage" in names and "Driver" in names for path, names in writers)


def make_driver():
    events = []
    driver = Driver.__new__(Driver)
    driver._open_stage = None
    driver.log = SimpleNamespace(event=lambda name, **fields: events.append((name, fields)))
    return driver, events


def test_nested_stage_is_rejected_and_end_preserves_fields():
    driver, events = make_driver()
    with driver.stage(stem="owner", attempt=3, surface="author", run_seq=7) as stage:
        with pytest.raises(ValueError, match="owner.*author"):
            with driver.stage(stem="nested", attempt=4, surface="review"):
                pass
        stage.end("ok", calls=2)
    assert events == [
        ("stage_start", dict(stem="owner", attempt=3, surface="author", run_seq=7)),
        ("stage_end", dict(stem="owner", attempt=3, surface="author", outcome="ok", calls=2)),
    ]


@pytest.mark.parametrize("error", [ValueError, asyncio.CancelledError])
def test_stage_clears_after_exception_or_cancellation(error):
    driver, events = make_driver()
    with pytest.raises(error):
        with driver.stage(stem="first", attempt=1, surface="implement"):
            raise error()
    with driver.stage(stem="second", attempt=2, surface="review"):
        pass
    assert events == [
        ("stage_start", dict(stem="first", attempt=1, surface="implement")),
        ("stage_start", dict(stem="second", attempt=2, surface="review")),
    ]
