import asyncio
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from chupa import requisition


def entry(path, status="unaffected", reason="test:7 remains true"):
    return {"path": path, "status": status, "reason": reason}


def reply(dependents=None):
    data = {"verdict": "approve", "summary": "reviewed", "findings": []}
    if dependents is not None:
        data["dependents"] = dependents
    return data


def test_dependent_accounting():
    paths = {"tests/a.py", "tests/b.py"}
    fence = ("src/a.py", "tests/b.py")
    valid = requisition.RequisitionReply.model_validate(reply([entry("tests/a.py"), entry("tests/b.py", "fenced")]))
    assert requisition.dependent_errors(valid, paths, fence) == []
    for entries, expected in [
        ([entry("tests/a.py")], "missing dependent: tests/b.py"),
        ([entry("tests/a.py"), entry("tests/b.py"), entry("tests/c.py")], "extra dependent: tests/c.py"),
        ([entry("tests/a.py", "fenced"), entry("tests/b.py")], "wrongly fenced dependent: tests/a.py"),
        ([entry("tests/a.py"), entry("tests/a.py"), entry("tests/b.py")], "duplicate dependent: tests/a.py"),
    ]:
        assert expected in requisition.dependent_errors(requisition.RequisitionReply.model_validate(reply(entries)), paths, fence)
    with pytest.raises(ValidationError):
        requisition.RequisitionReply.model_validate(reply([entry("tests/a.py", reason="  ")]))
    assert requisition.dependent_errors(requisition.RequisitionReply.model_validate(reply()), set(), fence) == []


class MemoryPath:
    def __init__(self, name="", files=None):
        self.name = name
        self.files = files or {}

    def __truediv__(self, name):
        return MemoryPath(f"{self.name}/{name}".strip("/"), self.files)

    def rglob(self, pattern):
        assert pattern == "*.py"
        return [MemoryPath(name, self.files) for name in self.files if name.startswith(self.name + "/") and name.endswith(".py")]

    def relative_to(self, repo):
        return MemoryPath(self.name.removeprefix(repo.name + "/"))

    def as_posix(self):
        return self.name

    def read_text(self):
        return self.files.get(self.name, "spec")


def test_test_sources_reads_relative_paths():
    repo = MemoryPath("repo", {"repo/tests/integration/test_a.py": "fixture A", "repo/tests/test_b.py": "fixture B", "repo/tests/note.txt": "ignored"})
    assert requisition.test_sources(repo) == {"tests/integration/test_a.py": "fixture A", "tests/test_b.py": "fixture B"}


@pytest.mark.parametrize("data_file", [False, True])
def test_review_retries_missing_dependent(monkeypatch, data_file):
    fence = ("hosts/fixture/data.json",) if data_file else ("src/a.py",)
    test = "tests/integration/test_a.py"
    sources = Mock(return_value={test: "hosts/fixture/data.json", "tests/integration/test_b.py": "unrelated"})
    monkeypatch.setattr(requisition, "test_sources", sources)
    monkeypatch.setattr(requisition, "review_target", lambda *args: SimpleNamespace(scope_fence=fence))
    monkeypatch.setattr(requisition, "_base_render", lambda *args: "base")
    monkeypatch.setattr(requisition, "load_spec", lambda text: SimpleNamespace(meta=SimpleNamespace(version="1.0", effort="high")))
    renders = []
    monkeypatch.setattr(requisition, "render", lambda spec, values: renders.append(values.copy()) or "prompt")
    calls = []

    async def call(*args, **kwargs):
        calls.append(kwargs)
        result = reply() if len(calls) == 1 else reply([entry(test)])
        return dict(text=json.dumps(result), input_tokens=1, output_tokens=2, provider="fake", model="m", usd=0.1)

    async def race(fn, timeout):
        return await fn()

    monkeypatch.setattr(requisition, "llm_call", call)
    driver = SimpleNamespace(
        retry_cap=1, spool=SimpleNamespace(write=lambda *args: None), _active=True, begin_watch=lambda **kw: None, race=race, effects=None, watched_llm=lambda: None, redactor=None
    )
    mapping = None if data_file else MemoryPath("map", {"map": json.dumps({"files": {"src/a.py": [test]}})})
    verdict = asyncio.run(
        requisition.review_ticket(
            driver,
            repo=MemoryPath(),
            stem="one",
            text="ticket",
            specs_dir=MemoryPath(),
            coverage_map=mapping,
            tier="high",
            stem_slot="slot",
            run_seq=1,
            attempt=1,
            call_seq=1,
            expected_budget="surface",
            prior="first",
        )
    )
    assert verdict.verdict == "approve" and len(calls) == 2
    assert test in renders[1]["retry_findings"]
    if data_file:
        sources.assert_called_once()
        assert renders[0]["coverage_dependents"] == f"{test}: reads hosts/fixture/data.json"
    else:
        sources.assert_not_called()
        assert renders[0]["coverage_dependents"] == f"{test}: runs src/a.py"
