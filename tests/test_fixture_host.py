"""Direct scaffold evidence, deliberately below production host-loop evidence."""

import asyncio
import json
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from types import ModuleType, SimpleNamespace

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from chupa.artifacts import NonBlank, ReviewVerdict
from chupa.author import AuthorReply
from chupa.config import load_config
from chupa.git import Git
from chupa.hostfiles import classify_core
from chupa.llm import LLMRequest
from chupa.providers import ClaudeAdapter, ProviderCallError, ProviderLLM
from chupa.seams import LocalFileSystem, SubprocessExec
from chupa.specs import (
    ENTRY_PARTS, PlanContractError, entry_unit_gap, load_spec, render,
    required_units, resolve_plan_contract,
)
from chupa.stages import ImplementReply
from chupa.tickets import parse_ticket, stamp, validate_ticket
from chupa.triage import TriageReply

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "hosts/fixture"
PLAN = (ROOT / "CHUPA_PLAN.md").read_text()
# Load the fixture constructor without generating bytecode in committed inputs.
scaffold = ModuleType("fixture_scaffold")
scaffold.__file__ = str(SOURCE / "scaffold.py")
exec(compile((SOURCE / "scaffold.py").read_text(), scaffold.__file__, "exec"), scaffold.__dict__)
SCENARIOS = ("merge-add", "merge-bonus", "merge-floor", "regression", "escape")
SURFACES = {"author": AuthorReply, "implement": ImplementReply,
            "review": ReviewVerdict, "triage": TriageReply}


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


INPUT_BYTES = snapshot(SOURCE)
ENGINE_BYTES = snapshot(ROOT / "chupa")


@pytest.fixture
def host(tmp_path):
    return scaffold.copy_host(tmp_path / "host")


def environment(host, **extra):
    return {"PATH": str(host / "bin") + ":" + str(Path(sys.executable).parent) + ":/usr/bin:/bin",
            "PYTHONDONTWRITEBYTECODE": "1", "CHUPA_FIXTURE_ROOT": str(host), **extra}


def run(host, argv):
    return asyncio.run(SubprocessExec().run(argv, cwd=host, env=environment(host), timeout=10))


def replay(host, name):
    return run(host, [sys.executable, "replay.py", f"evidence/{name}.json"])


def implement(host, name):
    return scaffold.scripted_reply(host, name, "implement", "fixture edit", True)


def test_fixture_host_entry_units():
    own = "19.P6.fixture-host-scaffold"
    cited = ("19.P6.host-contract-doc", "19.P6.core-drift-activation")
    ticket = parse_ticket("fixture-host-scaffold",
        (ROOT / "tickets/fixture-host-scaffold/ticket.md").read_text(), ROOT, plan=PLAN)
    assert required_units(PLAN, ticket.stem, ticket.plan_contract) == (own, *cited)
    assert required_units(PLAN, "later-consumer", (own, *cited)) == (own, *cited)
    resolved = resolve_plan_contract(PLAN, (*ticket.plan_contract, own))
    assert ENTRY_PARTS == ("Owner", "Records", "Observable", "Tests")
    for uid in (own, *cited):
        assert resolved.count(f"### {uid} ") == 1
        assert entry_unit_gap(PLAN, uid) is None
        unit = resolve_plan_contract(PLAN, (uid,))
        for part in ENTRY_PARTS:
            for replacement in ("", f"- **{part}:**"):
                broken = re.sub(rf"^- \*\*{part}:\*\*.*$", replacement, unit, flags=re.M)
                assert part in entry_unit_gap(broken, uid)
        for broken in ("", unit + unit):
            assert entry_unit_gap(broken, uid)
            with pytest.raises(PlanContractError):
                resolve_plan_contract(broken, (uid,))


def test_fixture_profile_loads(host):
    cfg = load_config(None, cwd=host)
    assert cfg.schema_version == 1
    assert cfg.state_dir == host / ".chupa/state"
    assert cfg.worktree_root == host / ".chupa/worktrees"
    assert cfg.report_inbox == host / "reports"
    assert cfg.routing_default_tier == "medium"
    assert [(r.tier, r.surface, r.candidates[0].provider) for r in cfg.routing] == [
        ("medium", surface, "claude") for surface in SURFACES]
    assert cfg.providers[0].auth is None
    assert cfg.providers[0].package == "@anthropic-ai/claude-code"
    assert cfg.review.mechanical[0].model_dump() == {
        "code": "fixture-smoke", "argv": ["python", "check.py"], "trigger": "always", "severity": "hard"}
    assert cfg.review.surfaces == [] and cfg.review.gate_severity == {} and cfg.review.trigger_map == {}
    assert cfg.merge.safety_checks == ["fixture-smoke"] and cfg.merge.strategies == []
    assert cfg.engine_plane_safety_inventory == [
        "config.yaml", "CLAUDE.md", "bin/", "scripts.json", "scaffold.py", "check.py", "regression_test.py"]
    assert classify_core((host / "CLAUDE.md").read_bytes()).state == "current"
    assert not cfg.state_dir.exists() and not cfg.worktree_root.exists()


def test_fixture_scenario_list_is_closed(host):
    rows = json.loads((host / "scripts.json").read_text())
    assert tuple(rows) == scaffold.SCENARIOS == SCENARIOS
    assert [row["kind"] for row in rows.values()] == ["machine_merge"] * 3 + ["regression", "escape"]
    assert len({json.dumps(rows[name]["edits"], sort_keys=True) for name in SCENARIOS[:3]}) == 3
    for name, row in rows.items():
        assert set(row) == {"kind", "responses", "edits", "checks", "evidence"}
        assert set(row["responses"]) == set(SURFACES)
        for surface, model in SURFACES.items():
            assert len(row["responses"][surface]) == 1
            model.model_validate(row["responses"][surface][0])
        authored = row["responses"]["author"][0]
        ticket = validate_ticket(authored["stem"], stamp(stamp(authored["ticket"], "source", "box:bug_report"),
                                 "state", "draft"), host)
        assert ticket.scope_fence == ("settings.json",)
        assert set(row["edits"]) == {"settings.json"}
        assert row["checks"][0] == {"argv": ["python", "check.py"], "base_rc": 0, "head_rc": 0}
        for key in ("replay", "log", "report"):
            assert (host / row["evidence"][key]).is_file()
    with pytest.raises(ValueError, match="select a declared scenario"):
        scaffold.scenario(host, "unknown")


def test_fixture_replay_is_deterministic(host):
    for name in SCENARIOS:
        first = replay(host, name)
        assert first == replay(host, name)
        row = scaffold.scenario(host, name)
        assert first[0] == row["evidence"]["base_rc"]
        before = json.loads(first[1])
        assert before["defect"] == bool(first[0])
        for check in row["checks"]:
            assert run(host, [sys.executable, *check["argv"][1:]])[0] == check["base_rc"]
    # Each scenario starts from an independent base, rather than another fix's settings.
    for name in SCENARIOS:
        (host / "settings.json").write_bytes(INPUT_BYTES["settings.json"])
        implement(host, name)
        first = replay(host, name)
        assert first == replay(host, name)
        assert first[0] == scaffold.scenario(host, name)["evidence"]["head_rc"]
        for check in scaffold.scenario(host, name)["checks"]:
            assert run(host, [sys.executable, *check["argv"][1:]])[0] == check["head_rc"]
        expected_scores = {"merge-add": 3, "merge-bonus": 6, "merge-floor": 0, "regression": 3, "escape": 7}
        assert json.loads(first[1]) == {"final_state": {"score": expected_scores[name]}, "defect": name == "escape"}


def test_fixture_regression_exists_at_base(host):
    async def proof():
        git = Git(SubprocessExec(), env={**environment(host), "GIT_AUTHOR_NAME": "Fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid", "GIT_COMMITTER_NAME": "Fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}, timeout=10)
        await git.init(host, branch="main")
        await git.add(host, ["app.py", "settings.json", "regression_test.py"])
        await git.commit(host, "fixture defective base")
        base = await git.rev_parse(host, "HEAD")
        assert await git._run(host, "show", f"{base}:regression_test.py") == (host / "regression_test.py").read_text()
        # Existing tracked test, actual defective base and unchanged regression at fixed head.
        rc, out, err = await SubprocessExec().run([sys.executable, "regression_test.py"],
            cwd=host, env=environment(host), timeout=10)
        assert rc == 1 and "add must increase score by 3" in err
        implement(host, "regression")
        await git.add(host, ["settings.json"])
        await git.commit(host, "fixture scripted add repair")
        head = await git.rev_parse(host, "HEAD")
        assert await git.merge_base(host, base, head) == base
        assert await git.diff_names(host, base, head) == ["settings.json"]
        assert (await SubprocessExec().run([sys.executable, "regression_test.py"],
            cwd=host, env=environment(host), timeout=10))[0] == 0
    asyncio.run(proof())


def test_fixture_escape_is_machine_introduced(host):
    before = snapshot(host)
    assert run(host, [sys.executable, "check.py"])[0] == 0
    assert replay(host, "escape")[0] == 0
    ImplementReply.model_validate_json(implement(host, "escape"))
    after = snapshot(host)
    assert {p for p in before if before[p] != after[p]} == {"settings.json"}
    assert json.loads((host / "settings.json").read_text())["spend_sign"] == 1
    assert run(host, [sys.executable, "check.py"])[0] == 0
    assert replay(host, "escape")[0] == 1


# This local model is a scaffold check of Records, not an inbox implementation.
class Evidence(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    replay: str | None = None
    log: str | None = None


class PlayerReport(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    schema_version: int
    origin: str
    summary: NonBlank
    app_commit: NonBlank
    app_version: NonBlank
    implicated_paths: list[str] = []
    evidence: Evidence = Evidence()

    @field_validator("schema_version")
    @classmethod
    def version_one(cls, value):
        if value != 1:
            raise ValueError("use schema_version 1")
        return value


class SelfReport(PlayerReport):
    game_slug: NonBlank
    anomaly_code: NonBlank
    location: NonBlank


def relative_path(value):
    path = PurePosixPath(value)
    if not value.strip() or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError("use a repo-relative path inside the disposable host")
    return path


def validate_report(raw, host):
    if raw.get("origin") not in {"self_diagnosed", "player"}:
        raise ValueError("select self_diagnosed or player")
    report = (SelfReport if raw["origin"] == "self_diagnosed" else PlayerReport).model_validate(raw)
    for path in report.implicated_paths:
        relative_path(path)
    for kind, limit in (("replay", 1024 * 1024), ("log", 64 * 1024)):
        value = getattr(report.evidence, kind)
        if value is None:
            continue
        path = (host / relative_path(value)).resolve()
        if not path.is_relative_to(host.resolve()):
            raise ValueError("evidence escapes host; copy evidence inside the disposable host")
        metadata = path.stat()
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("evidence must be a regular file; attach a host-contained regular file")
        if metadata.st_size > limit:
            raise ValueError(f"{kind} exceeds {limit} bytes; attach a bounded excerpt")
        if kind == "replay":
            record = json.loads(path.read_bytes())
            if (not isinstance(record, dict) or not isinstance(record.get("initial_state"), dict)
                    or not isinstance(record.get("actions"), list)
                    or any(not isinstance(a, dict) for a in record["actions"])):
                raise ValueError("replay needs initial_state and an ordered actions list")
    return report


def test_fixture_reports_are_bounded(host, tmp_path):
    reports = [json.loads(p.read_text()) for p in sorted((host / "reports").glob("*.json"))]
    assert {validate_report(raw, host).origin for raw in reports} == {"self_diagnosed", "player"}
    player = next(r for r in reports if r["origin"] == "player")
    self_report = next(r for r in reports if r["origin"] == "self_diagnosed")
    minimal = {k: player[k] for k in ("schema_version", "origin", "summary", "app_commit", "app_version")}
    normalized = validate_report(minimal, host)
    assert normalized.implicated_paths == [] and normalized.evidence.model_dump() == {"replay": None, "log": None}
    assert validate_report({**minimal, "evidence": {}}, host).evidence == Evidence()
    assert validate_report({**minimal, "evidence": {"replay": None, "log": None}}, host).evidence == Evidence()
    bad = []
    for raw in (minimal, self_report):
        for field in ("summary", "app_commit", "app_version"):
            for value in ("", " \n ", None, 3):
                bad.append({**raw, field: value})
        for field in ("schema_version", "origin", "summary", "app_commit", "app_version"):
            bad.append({k: v for k, v in raw.items() if k != field})
    for field in ("game_slug", "anomaly_code", "location"):
        bad.extend([{**self_report, field: " "}, {k: v for k, v in self_report.items() if k != field},
                    {**minimal, field: "unexpected"}])
    bad.extend({**minimal, "schema_version": v} for v in (0, 2, -1, True, False, 1.0, "1", None))
    bad.extend([{**minimal, "origin": "unknown"}, {**minimal, "signature": "invented"},
                {**minimal, "extra": True}, {**minimal, "evidence": {"extra": "x"}},
                {**minimal, "evidence": None}, {**minimal, "implicated_paths": None}])
    for raw in bad:
        with pytest.raises((ValueError, ValidationError)):
            validate_report(raw, host)
    for value in ("../outside", "/absolute", "", "a/../../outside", "a\\b"):
        with pytest.raises(ValueError):
            validate_report({**minimal, "implicated_paths": [value]}, host)
        with pytest.raises(ValueError):
            validate_report({**minimal, "evidence": {"log": value}}, host)
    outside = tmp_path / "outside.log"
    outside.write_text("untrusted")
    (host / "outside-link").symlink_to(outside)
    for value in ("outside-link", "evidence", "missing"):
        with pytest.raises((ValueError, OSError)):
            validate_report({**minimal, "evidence": {"log": value}}, host)
    boundary = host / "evidence/boundary"
    for kind, cap in (("replay", 1024 * 1024), ("log", 64 * 1024)):
        data = b'{"initial_state":{"score":0},"actions":[]}' if kind == "replay" else b"log"
        boundary.write_bytes(data + b" " * (cap - len(data)))
        raw = {**minimal, "evidence": {kind: "evidence/boundary"}}
        validate_report(raw, host)
        boundary.write_bytes(boundary.read_bytes() + b" ")
        with pytest.raises(ValueError, match="exceeds"):
            validate_report(raw, host)
    for record in ({}, {"initial_state": {}, "actions": {}}, {"initial_state": [], "actions": []},
                   {"initial_state": {}, "actions": [1]}):
        boundary.write_text(json.dumps(record))
        with pytest.raises(ValueError, match="ordered actions"):
            validate_report({**minimal, "evidence": {"replay": "evidence/boundary"}}, host)


class RecordedExec(SubprocessExec):
    def __init__(self, host):
        self.host, self.calls = host, []

    async def run(self, argv, **kwargs):
        assert argv[0] in {"claude", "pnpm"}
        assert kwargs["cwd"] == self.host
        assert set(kwargs["env"]) <= set(environment(self.host)) | {
            "CHUPA_FIXTURE_SCENARIO", "CHUPA_FIXTURE_SURFACE"}
        assert all("secret" not in v.lower() for v in kwargs["env"].values())
        self.calls.append((list(argv), dict(kwargs)))
        return await super().run(argv, **kwargs)


def test_fixture_cli_adapter_roundtrip(host):
    async def proof():
        cfg = load_config(None, cwd=host)
        exec_ = RecordedExec(host)
        session = SimpleNamespace(active=False, thresh=SimpleNamespace(configure=lambda cfg: None),
                                  exclusions=lambda: set(), preflight_passed=lambda: None)
        env = environment(host)
        llm = ProviderLLM(cfg, exec_=exec_, fs=LocalFileSystem(), env=env, cwd=host, timeout=10, session=session)
        assert type(llm._adapters["claude"]) is ClaudeAdapter
        assert await llm.preflight() == [] and llm.preflight_notices == []
        assert exec_.calls[0][0] == ["claude", "--version"]
        assert exec_.calls[1][0] == ["pnpm", "view", "@anthropic-ai/claude-code", "version"]
        assert exec_.calls[2][1]["stdin_path"].read_text() == "Reply with the single word ok."
        base_settings = (host / "settings.json").read_bytes()
        for name in SCENARIOS:
            (host / "settings.json").write_bytes(base_settings)
            for surface, model in SURFACES.items():
                env.update(CHUPA_FIXTURE_SCENARIO=name, CHUPA_FIXTURE_SURFACE=surface)
                spec = load_spec((ROOT / "specs" / f"{surface}.md").read_text())
                prompt = render(spec, {key: "fixture data " + key for key in spec.inputs})
                before = (host / "settings.json").read_bytes()
                result = await llm.call(LLMRequest(surface, prompt, "medium", "medium", name,
                                                 host if surface == "implement" else None))
                assert result.usd == 0 and result.provider == "claude" and result.model == "fixture"
                model.model_validate_json(result.text)
                argv, kwargs = exec_.calls[-1]
                assert prompt not in argv and kwargs["stdin_path"].read_text() == prompt
                assert (host / ".fixture-runtime" / f"{name}-{surface}-0.prompt").read_text() == prompt
                if surface == "implement":
                    assert "bypassPermissions" in argv
                    assert json.loads((host / "settings.json").read_text()) == {
                        **json.loads(base_settings), **scaffold.scenario(host, name)["edits"]["settings.json"]}
                else:
                    assert "--allowedTools" in argv and (host / "settings.json").read_bytes() == before
        env.update(CHUPA_FIXTURE_SCENARIO="unknown", CHUPA_FIXTURE_SURFACE="review")
        with pytest.raises(ProviderCallError, match="select a declared scenario"):
            await llm.call(LLMRequest("review", "unknown", "medium", "low", None, None))
        env["CHUPA_FIXTURE_SCENARIO"] = "escape"
        with pytest.raises(ProviderCallError, match="replenish.*declared responses"):
            await llm.call(LLMRequest("review", "exhausted", "medium", "low", None, None))
        assert not (cfg.state_dir / "journal").exists()
    asyncio.run(proof())


def test_fixture_scaffold_is_dormant(host):
    assert snapshot(SOURCE) == INPUT_BYTES and snapshot(ROOT / "chupa") == ENGINE_BYTES
    # Missing runtime marker refuses even an otherwise valid script before any write.
    with pytest.raises(ValueError, match="disposable host"):
        scaffold.scripted_reply(SOURCE, "merge-add", "implement", "prompt", True)
    assert snapshot(SOURCE) == INPUT_BYTES
    with pytest.raises(ValueError, match="outside the committed fixture"):
        scaffold.copy_host(SOURCE / "copy")
    before = snapshot(host)
    implement(host, "merge-add")
    after = snapshot(host)
    assert {p for p in before if before[p] != after[p]} == {"settings.json"}
    assert {p for p in after if p not in before} <= {
        ".fixture-runtime/cursors.json", ".fixture-runtime/merge-add-implement-0.prompt"}
    assert not (host / ".chupa").exists()
    # Production code has no edge to these host inputs (either import idiom or path lookup).
    for path, data in ENGINE_BYTES.items():
        if path.endswith(".py"):
            assert b"hosts.fixture" not in data and b"hosts/fixture" not in data
    for path in after:
        assert not any(word in Path(path).parts for word in ("GO", "journal", "host-loop-report.json"))
    assert not any("serve" in call for row in json.loads((host / "scripts.json").read_text()).values()
                   for check in row["checks"] for call in check["argv"])
    assert snapshot(SOURCE) == INPUT_BYTES and snapshot(ROOT / "chupa") == ENGINE_BYTES
