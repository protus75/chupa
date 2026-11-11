# Review: snag

The production change, docs and most tests match the ticket, but the unit test test_status_verb_passes_alive drives the real `_status`, so it reads a spec file from disk and uses a wall-clock clock, which unit tests may not do.

## Findings

- [logic] tests/unit/test_stale_running.py:141 test_status_verb_passes_alive calls the real `entry._status`, which runs `load_spec((runner.SPECS_DIR / "retro.md").read_text())` (chupa/__main__.py `_status`). That makes this unit test read a file from disk. The ticket asks for this test to use fakes, and unit tests must not read or write disk. (do instead: Before calling `_status`, monkeypatch `runner.SPECS_DIR` to a fake whose `/ "retro.md"` returns an object with `read_text()` giving a fixed string. Also monkeypatch `chupa.specs.load_spec`, which `_status` imports at call time, to return `SimpleNamespace(meta=SimpleNamespace(version="v"))`. Then no file is read.)
- [logic] tests/unit/test_stale_running.py:136 The fake checkout's clock is `lambda: __import__("datetime").datetime.now()`, so `_status` reads wall-clock time while this unit test runs. Unit tests must not depend on wall-clock time. (do instead: Use a fixed clock, for example `clock=lambda: datetime(2026, 1, 1, tzinfo=UTC)`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "7bb1e8ae386fd6026d5b4b24e8170d76f10048cd",
  "stem": "stale-running-after-kill",
  "reviewed_sha": "7bb1e8ae386fd6026d5b4b24e8170d76f10048cd",
  "summary": "The production change, docs and most tests match the ticket, but the unit test test_status_verb_passes_alive drives the real `_status`, so it reads a spec file from disk and uses a wall-clock clock, which unit tests may not do.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/unit/test_stale_running.py",
      "line": 141,
      "message": "test_status_verb_passes_alive calls the real `entry._status`, which runs `load_spec((runner.SPECS_DIR / \"retro.md\").read_text())` (chupa/__main__.py `_status`). That makes this unit test read a file from disk. The ticket asks for this test to use fakes, and unit tests must not read or write disk.",
      "paved_road": "Before calling `_status`, monkeypatch `runner.SPECS_DIR` to a fake whose `/ \"retro.md\"` returns an object with `read_text()` giving a fixed string. Also monkeypatch `chupa.specs.load_spec`, which `_status` imports at call time, to return `SimpleNamespace(meta=SimpleNamespace(version=\"v\"))`. Then no file is read.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "tests/unit/test_stale_running.py",
      "line": 136,
      "message": "The fake checkout's clock is `lambda: __import__(\"datetime\").datetime.now()`, so `_status` reads wall-clock time while this unit test runs. Unit tests must not depend on wall-clock time.",
      "paved_road": "Use a fixed clock, for example `clock=lambda: datetime(2026, 1, 1, tzinfo=UTC)`.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
