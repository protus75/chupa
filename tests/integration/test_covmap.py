import json
from types import SimpleNamespace

import pytest

from chupa.covmap import build, reduce_map
from chupa.runner import Refusal

REPORT = {
    "files": {
        "chupa/a.py": {"contexts": {"1": ["tests/test_b.py::test_b|run", "tests/test_a.py::test_a|run", "module"], "2": ["tests/test_b.py::test_b|setup"]}},
        "chupa/b.py": {"contexts": {}},
    }
}


def test_reduce_map():
    assert reduce_map(REPORT) == {"chupa/a.py": ["tests/test_a.py", "tests/test_b.py"], "chupa/b.py": []}


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["success", "exit", "missing", "invalid"])
async def test_build(tmp_path, case):
    report = tmp_path / "raw.json"
    state = tmp_path / "state"
    config = SimpleNamespace(review=SimpleNamespace(coverage_map=SimpleNamespace(argv=["tests-command"], report="raw.json")), state_dir=state)

    class Exec:
        async def run(self, argv, *, cwd, env, timeout):
            assert argv == ["tests-command"] and cwd == tmp_path
            if case in {"success", "invalid"}:
                report.write_text(json.dumps(REPORT) if case == "success" else "{}")
            return (1 if case == "exit" else 0, "", "")

    class Git:
        async def rev_parse(self, repo, ref):
            assert repo == tmp_path and ref == "main"
            return "main-sha"

    class FS:
        def __init__(self):
            self.files = {state / "coverage-map.json": b"previous"}

        def publish(self, path, data):
            self.files[path] = data

        def replace(self, src, dst):
            self.files[dst] = self.files.pop(src)

    fs = FS()
    if case == "success":
        await build(repo=tmp_path, config=config, exec_=Exec(), git=Git(), fs=fs, env={})
        assert json.loads(fs.files[state / "coverage-map.json"]) == {"sha": "main-sha", "files": {"chupa/a.py": ["tests/test_a.py", "tests/test_b.py"], "chupa/b.py": []}}
    else:
        with pytest.raises(Refusal):
            await build(repo=tmp_path, config=config, exec_=Exec(), git=Git(), fs=fs, env={})
        assert fs.files == {state / "coverage-map.json": b"previous"}
    assert not report.exists()
