import asyncio
import json
import textwrap
from pathlib import Path

import pytest

from chupa.config import ConfigError, load_config
from chupa.llm import LLMRequest
from chupa.providers import (
    PLACEHOLDER,
    ProviderCallError,
    ProviderLLM,
    ProviderSetupError,
    child_env,
    resolve,
)
from chupa.seams import GroupExec, LocalFileSystem

ROOT = Path(__file__).resolve().parent.parent

CONFIG = textwrap.dedent(
    """\
    schema_version: 1
    state_dir: state
    providers:
      - name: claude
        kind: cli
        package: test-cli
        auth: CLAUDE_KEY
        models_by_tier: {low: c-low, medium: c-med, high: c-high, max: c-max}
        limits: {concurrency: 1}
      - name: codex
        kind: cli
        package: test-cli
        auth: CODEX_KEY
        models_by_tier: {low: x-low, medium: x-med, high: x-high, max: x-max}
        limits: {concurrency: 1, est_cost_per_call_usd: 1.5}
    routing:
      - {tier: medium, surface: implement, candidates: [{provider: codex}, {provider: claude}]}
      - {tier: high, surface: implement, candidates: [{provider: claude}]}
      - {tier: medium, surface: review, candidates: [{provider: claude, model: c-max}, {provider: codex}]}
      - {tier: low, surface: review, candidates: [{provider: codex}]}
    review: {}
    merge: {}
    engine_plane_safety_inventory: []
    """
)

ENV = {"PATH": "/usr/bin", "HOME": "/home/op", "CLAUDE_KEY": "sk-claude-secret", "CODEX_KEY": "sk-codex-secret"}


def config(tmp_path: Path, text: str = CONFIG):
    (tmp_path / "config.yaml").write_text(text)
    return load_config(None, cwd=tmp_path)


class FakeExec:
    """Scripted subprocess: records each invocation and what its stdin file held at spawn."""

    def __init__(self, *responses: tuple[int, str, str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict] = []
        self.killed: list[int] = []
        self.hang: asyncio.Event | None = None

    async def run(self, argv, *, cwd, env, timeout, stdin_path=None, on_spawn=None):
        self.calls.append(
            {"argv": list(argv), "cwd": cwd, "env": dict(env), "stdin": Path(stdin_path).read_text(), "timeout": timeout}
        )
        if on_spawn is not None:
            on_spawn(4242)
        if self.hang is not None:
            await self.hang.wait()
            return -9, "", "killed"
        return self.responses.pop(0)

    def kill_group(self, pgid: int) -> None:
        self.killed.append(pgid)
        if self.hang is not None:
            self.hang.set()


def llm(cfg, exec_: FakeExec, tmp_path: Path) -> ProviderLLM:
    return ProviderLLM(cfg, exec_=exec_, fs=LocalFileSystem(), env=ENV, cwd=tmp_path / "checkout", timeout=600)


def req(surface: str, tier="medium", worktree=None, rendered="do the thing", effort="high") -> LLMRequest:
    return LLMRequest(surface=surface, rendered=rendered, tier=tier, effort=effort, ticket="t-1", worktree=worktree)


def jsonl(*events: dict) -> str:
    return "".join(json.dumps(e) + "\n" for e in events)


def claude_ok(text="done", cost=0.42) -> str:
    return jsonl(
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "working"}]}},
        {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "result": text,
            "total_cost_usd": cost,
            "usage": {
                "input_tokens": 10,
                "cache_creation_input_tokens": 5,
                "cache_read_input_tokens": 100,
                "output_tokens": 7,
            },
        },
    )


def codex_ok(text="patched") -> str:
    return jsonl(
        {"type": "thread.started", "thread_id": "th"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"id": "i0", "type": "agent_message", "text": "first"}},
        {"type": "item.completed", "item": {"id": "i1", "type": "command_execution", "command": "ls"}},
        {"type": "item.completed", "item": {"id": "i2", "type": "agent_message", "text": text}},
        {"type": "turn.completed", "usage": {"input_tokens": 300, "cached_input_tokens": 200, "output_tokens": 40}},
    )


def call(cfg, exec_, tmp_path, request):
    return asyncio.run(llm(cfg, exec_, tmp_path).call(request))


# --- registry + routing parse ---


def test_routing_takes_first_candidate_and_inherits_models_by_tier(tmp_path):
    cfg = config(tmp_path)
    served = resolve(cfg, "medium", "implement")
    assert (served.provider.name, served.model) == ("codex", "x-med")
    served = resolve(cfg, "high", "implement")
    assert (served.provider.name, served.model) == ("claude", "c-high")


def test_routing_candidate_model_pin_overrides_models_by_tier(tmp_path):
    served = resolve(config(tmp_path), "medium", "review")
    assert (served.provider.name, served.model) == ("claude", "c-max")


def test_routing_hole_is_a_setup_refusal_naming_the_row(tmp_path):
    with pytest.raises(ProviderSetupError, match="tier 'max', surface 'implement'"):
        resolve(config(tmp_path), "max", "implement")


def test_placeholder_row_is_refused_before_any_call(tmp_path):
    cfg = config(tmp_path, CONFIG.replace("x-med", PLACEHOLDER))
    exec_ = FakeExec()
    with pytest.raises(ProviderSetupError, match="Phase 1 prerequisites"):
        call(cfg, exec_, tmp_path, req("implement", worktree=tmp_path))
    assert exec_.calls == []


def test_implement_routed_to_api_provider_fails_config_load(tmp_path):
    text = CONFIG.replace("name: codex\n    kind: cli", "name: codex\n    kind: api")
    (tmp_path / "config.yaml").write_text(text)
    with pytest.raises(ConfigError) as exc:
        load_config(None, cwd=tmp_path)
    assert exc.value.key == "routing.0.candidates.0.provider"
    assert "kind: cli" in str(exc.value)


def test_unknown_cli_provider_has_no_adapter(tmp_path):
    cfg = config(tmp_path, CONFIG.replace("name: codex", "name: gemini").replace("provider: codex", "provider: gemini"))
    with pytest.raises(ProviderSetupError, match="no shipped cli adapter"):
        llm(cfg, FakeExec(), tmp_path)


def test_no_cost_stream_without_estimate_is_a_setup_refusal(tmp_path):
    cfg = config(tmp_path, CONFIG.replace(", est_cost_per_call_usd: 1.5", ""))
    with pytest.raises(ProviderSetupError, match="est_cost_per_call_usd"):
        llm(cfg, FakeExec(), tmp_path)


def test_instance_config_routes_every_tier_for_review_author_implement():
    cfg = load_config(None, cwd=ROOT)
    assert cfg.state_dir == ROOT / ".chupa" / "state"
    for tier in ("low", "medium", "high", "max"):
        implement = resolve(cfg, tier, "implement")
        assert implement.provider.name == "codex" and implement.provider.kind == "cli"
        assert implement.model == getattr(implement.provider.models_by_tier, tier)
        author = resolve(cfg, tier, "author")
        assert author.provider.name == "claude"
        assert author.model == getattr(author.provider.models_by_tier, tier)
        review = resolve(cfg, tier, "review")
        assert (review.provider.name, review.model) == ("claude", cfg.providers[0].models_by_tier.max)
    llm(cfg, FakeExec(), ROOT)  # every provider has an adapter and its cost floor


# --- key scoping ---


def test_non_llm_child_env_carries_no_provider_key(tmp_path):
    env = child_env(ENV, config(tmp_path))
    assert env == {"PATH": "/usr/bin", "HOME": "/home/op"}


def test_llm_call_env_restores_only_the_serving_providers_key(tmp_path):
    cfg = config(tmp_path)
    exec_ = FakeExec((0, codex_ok(), ""), (0, claude_ok(), ""))
    client = llm(cfg, exec_, tmp_path)
    asyncio.run(client.call(req("implement", worktree=tmp_path)))
    asyncio.run(client.call(req("review")))
    codex_env, claude_env = exec_.calls[0]["env"], exec_.calls[1]["env"]
    assert codex_env == {"PATH": "/usr/bin", "HOME": "/home/op", "CODEX_KEY": "sk-codex-secret"}
    assert claude_env == {"PATH": "/usr/bin", "HOME": "/home/op", "CLAUDE_KEY": "sk-claude-secret"}


def test_serving_key_unset_is_a_setup_refusal(tmp_path):
    env = {k: v for k, v in ENV.items() if k != "CODEX_KEY"}
    with pytest.raises(ProviderSetupError, match="CODEX_KEY"):
        child_env(env, config(tmp_path), config(tmp_path).providers[1])


def test_echoed_secret_is_redacted_from_result_and_both_capture_sinks(tmp_path):
    cfg = config(tmp_path)
    leak = "env says sk-codex-secret and sk-claude-secret"
    exec_ = FakeExec((0, codex_ok(leak), "stderr sk-codex-secret"))
    result = call(cfg, exec_, tmp_path, req("implement", worktree=tmp_path))
    assert result.text == "env says [REDACTED:CODEX_KEY] and [REDACTED:CLAUDE_KEY]"
    captured = "".join(p.read_text() for p in (cfg.state_dir / "spools").rglob("*") if p.is_file())
    assert "sk-" not in captured
    assert "[REDACTED:CODEX_KEY]" in captured


# --- claude adapter live contract ---


def test_claude_implement_gets_the_write_grant_in_the_worktree(tmp_path):
    cfg = config(tmp_path)
    exec_ = FakeExec((0, claude_ok(), ""))
    worktree = tmp_path / "wt"
    call(cfg, exec_, tmp_path, req("implement", tier="high", worktree=worktree))
    inv = exec_.calls[0]
    assert inv["argv"] == [
        "claude", "-p", "--output-format", "stream-json", "--verbose", "--model", "c-high",
        "--permission-mode", "bypassPermissions",
    ]
    assert inv["cwd"] == worktree


def test_claude_read_only_surface_gets_the_read_tool_allowlist_and_no_grant(tmp_path):
    cfg = config(tmp_path)
    exec_ = FakeExec((0, claude_ok(), ""))
    call(cfg, exec_, tmp_path, req("review", worktree=tmp_path / "wt"))
    inv = exec_.calls[0]
    assert inv["argv"][-5:] == ["--allowedTools", "Read", "Grep", "Glob", "LS"]
    assert "bypassPermissions" not in inv["argv"]
    assert inv["cwd"] == tmp_path / "checkout"


def test_claude_prompt_goes_on_stdin_never_argv(tmp_path):
    exec_ = FakeExec((0, claude_ok(), ""))
    call(config(tmp_path), exec_, tmp_path, req("review", rendered="PROMPT-BODY " * 50))
    assert exec_.calls[0]["stdin"] == "PROMPT-BODY " * 50
    assert not any("PROMPT-BODY" in a for a in exec_.calls[0]["argv"])


def test_claude_text_usage_and_cost_come_from_the_result_event(tmp_path):
    result = call(config(tmp_path), FakeExec((0, claude_ok("verdict", 0.42), "")), tmp_path, req("review"))
    assert (result.text, result.input_tokens, result.output_tokens) == ("verdict", 115, 7)
    assert (result.provider, result.model, result.usd) == ("claude", "c-max", 0.42)


def test_claude_result_without_cost_falls_back_to_estimate_else_fails_closed(tmp_path):
    out = claude_ok().replace('"total_cost_usd": 0.42, ', "")
    with pytest.raises(ProviderCallError, match="est_cost_per_call_usd"):
        call(config(tmp_path), FakeExec((0, out, "")), tmp_path, req("review"))
    cfg = config(tmp_path, CONFIG.replace("limits: {concurrency: 1}", "limits: {concurrency: 1, est_cost_per_call_usd: 2.0}"))
    assert call(cfg, FakeExec((0, out, "")), tmp_path, req("review")).usd == 2.0


@pytest.mark.parametrize(
    "rc,out",
    [
        (1, ""),
        (0, jsonl({"type": "system", "subtype": "init"})),
        (0, jsonl({"type": "result", "subtype": "error_max_turns", "is_error": True, "result": ""})),
    ],
)
def test_claude_failure_shapes_raise_call_error(tmp_path, rc, out):
    with pytest.raises(ProviderCallError):
        call(config(tmp_path), FakeExec((rc, out, "boom")), tmp_path, req("review"))


# --- codex adapter live contract ---


def test_codex_implement_gets_the_write_grant_in_the_worktree(tmp_path):
    cfg = config(tmp_path)
    exec_ = FakeExec((0, codex_ok(), ""))
    worktree = tmp_path / "wt"
    call(cfg, exec_, tmp_path, req("implement", worktree=worktree, effort="high"))
    inv = exec_.calls[0]
    assert inv["argv"] == [
        "codex", "exec", "--json", "-m", "x-med", "-c", "model_reasoning_effort=high",
        "--dangerously-bypass-approvals-and-sandbox", "-",
    ]
    assert inv["cwd"] == worktree
    assert inv["stdin"] == "do the thing"


def test_codex_read_only_surface_is_sandboxed_read_only_with_no_approvals(tmp_path):
    exec_ = FakeExec((0, codex_ok(), ""))
    call(config(tmp_path), exec_, tmp_path, req("review", tier="low", effort="low"))
    inv = exec_.calls[0]
    assert inv["argv"] == [
        "codex", "exec", "--json", "-m", "x-low", "-c", "model_reasoning_effort=low",
        "--sandbox", "read-only", "-c", "approval_policy=never", "-",
    ]
    assert "--dangerously-bypass-approvals-and-sandbox" not in inv["argv"]
    assert inv["cwd"] == tmp_path / "checkout"


def test_codex_text_is_last_agent_message_usage_from_turn_completed_cost_is_the_estimate(tmp_path):
    result = call(config(tmp_path), FakeExec((0, codex_ok("final"), "")), tmp_path, req("implement", worktree=tmp_path))
    assert (result.text, result.input_tokens, result.output_tokens) == ("final", 300, 40)
    assert (result.provider, result.model, result.usd) == ("codex", "x-med", 1.5)


@pytest.mark.parametrize(
    "out",
    [
        jsonl({"type": "turn.started"}, {"type": "turn.failed", "error": {"message": "model unavailable"}}),
        jsonl({"type": "error", "message": "stream disconnected"}),
        jsonl({"type": "turn.started"}, {"type": "turn.completed", "usage": {}}),
    ],
)
def test_codex_failed_turn_raises_even_on_exit_zero(tmp_path, out):
    with pytest.raises(ProviderCallError):
        call(config(tmp_path), FakeExec((0, out, "")), tmp_path, req("implement", worktree=tmp_path))


def test_codex_nonzero_exit_carries_the_stream_failure_message(tmp_path):
    out = jsonl({"type": "turn.started"},
                {"type": "turn.failed", "error": {"message": "Selected model is at capacity."}})
    with pytest.raises(ProviderCallError, match="at capacity") as e:
        call(config(tmp_path), FakeExec((1, out, "")), tmp_path, req("implement", worktree=tmp_path))
    assert e.value.rc == 1


# --- shared base ---


def test_implement_without_worktree_is_refused_before_spawn(tmp_path):
    exec_ = FakeExec()
    with pytest.raises(ProviderSetupError, match="worktree"):
        call(config(tmp_path), exec_, tmp_path, req("implement"))
    assert exec_.calls == []


def test_abort_current_group_kills_the_active_child(tmp_path):
    exec_ = FakeExec()
    exec_.hang = asyncio.Event()
    assert isinstance(exec_, GroupExec)
    client = llm(config(tmp_path), exec_, tmp_path)

    async def scenario():
        task = asyncio.ensure_future(client.call(req("implement", worktree=tmp_path)))
        while not exec_.calls:
            await asyncio.sleep(0)
        client.abort_current()
        with pytest.raises(ProviderCallError):
            await task

    asyncio.run(scenario())
    assert exec_.killed == [4242]
    client.abort_current()  # idle: no active child, nothing to kill
    assert exec_.killed == [4242]


# --- provider preflight (section 6.11) ---


class PreflightExec:
    """Answers `--version`, `pnpm view`, and per-model probes; a model listed in `refused` fails its turn."""

    def __init__(self, versions: dict[str, str], latest: str, refused: frozenset[str] = frozenset()) -> None:
        self.versions, self.latest, self.refused = versions, latest, refused
        self.probed: list[str] = []

    async def run(self, argv, *, cwd, env, timeout, stdin_path=None, on_spawn=None):
        if argv[1:] == ["--version"]:
            return 0, self.versions[argv[0]], ""
        if argv[0] == "pnpm":
            return 0, self.latest + "\n", ""
        model = argv[argv.index("--model" if argv[0] == "claude" else "-m") + 1]
        self.probed.append(model)
        if model in self.refused:
            return 1, jsonl({"type": "error", "message": f"The '{model}' model is not supported"}), ""
        return 0, (claude_ok("ok") if argv[0] == "claude" else codex_ok("ok")), ""


CURRENT = {"claude": "1.2.3 (Claude Code)", "codex": "codex-cli 1.2.3"}


def preflight(tmp_path, exec_) -> list[str]:
    return asyncio.run(llm(config(tmp_path), exec_, tmp_path).preflight())


def test_preflight_passes_with_current_clis_and_every_routed_model_answering(tmp_path):
    exec_ = PreflightExec(CURRENT, "1.2.3")
    assert preflight(tmp_path, exec_) == []
    assert sorted(exec_.probed) == ["c-high", "c-max", "c-med", "x-low", "x-med"]  # each routed pair once


def test_preflight_refuses_a_stale_cli_with_its_upgrade_road(tmp_path):
    [problem] = preflight(tmp_path, PreflightExec({**CURRENT, "codex": "codex-cli 1.2.0"}, "1.2.3"))
    assert "codex 1.2.0 is not the latest release 1.2.3" in problem and "pnpm add -g test-cli@latest" in problem


def test_preflight_refuses_a_model_the_login_cannot_serve(tmp_path):
    [problem] = preflight(tmp_path, PreflightExec(CURRENT, "1.2.3", refused=frozenset({"x-low"})))
    assert "codex model 'x-low' failed its probe" in problem and "not supported" in problem


def test_cli_provider_must_declare_its_package(tmp_path):
    with pytest.raises(ConfigError, match="declares no `package`"):
        config(tmp_path, CONFIG.replace("    package: test-cli\n    auth: CODEX_KEY", "    auth: CODEX_KEY"))
