"""Fault-injection members for classified provider failures and redaction."""

import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from chupa.config import Candidate, Limits, ModelsByTier, Provider, Route
from chupa.journal import EventType
from chupa.providers import ProviderLLM
from chupa.seams import SubprocessExec
from eval.shakeout.bench import Bench
from eval.shakeout.run import Member, Observation
from eval.shakeout.stages import _finding, _terminal, _ticket


class _ScriptedProcess:
    """A production process seam that scripts only the Claude child and delegates git and checks."""

    def __init__(self, actions: Sequence[Callable[..., object]]) -> None:
        self._actions = iter(actions)
        self._delegate = SubprocessExec()

    async def run(self, argv, *, cwd: Path, env: Mapping[str, str], timeout: float | None,
                  stdin_path: Path | None = None, on_spawn=None, on_stdout_line=None) -> tuple[int, str, str]:
        if argv[1:] == ['--version'] or argv[0] == 'pnpm':
            return 0, '1.2.3', ''
        if stdin_path is not None and stdin_path.read_text() == 'Reply with the single word ok.':
            return _claude_result('ok')
        if argv[0] != "claude":
            return await self._delegate.run(argv, cwd=cwd, env=env, timeout=timeout,
                                            stdin_path=stdin_path, on_spawn=on_spawn, on_stdout_line=on_stdout_line)
        if on_spawn is not None:
            on_spawn(1)
        action = next(self._actions)
        result = action(cwd, env)
        if hasattr(result, "__await__"):
            result = await result
        if on_stdout_line is not None:
            for line in result[1].splitlines(keepends=True):
                on_stdout_line(line)
        return result

    def kill_group(self, pgid: int) -> None:
        self._delegate.kill_group(pgid)


def _claude_result(text: str) -> tuple[int, str, str]:
    return 0, json.dumps({
        "type": "result", "subtype": "success", "is_error": False, "result": text,
        "total_cost_usd": 0.0, "usage": {"input_tokens": 1, "output_tokens": 1},
    }) + "\n", ""


def _provider_config(bench: Bench, *, auth: str | None = None):
    provider = Provider(
        name="claude", kind="cli", auth=auth, package="@anthropic-ai/claude-code",
        models_by_tier=ModelsByTier(low="claude", medium="claude", high="claude", max="claude"),
        limits=Limits(concurrency=1),
    )
    routes = [
        Route(tier="medium", surface=surface, candidates=[Candidate(provider="claude")])
        for surface in ("implement", "review", "diagnose")
    ]
    return bench.config.model_copy(update={"providers": [provider], "routing": routes})


def _use_provider(bench: Bench, config, process: _ScriptedProcess, env: Mapping[str, str]) -> None:
    bench.process = process
    bench.env = env
    bench.configure(config)
    bench.llm = ProviderLLM(config, exec_=process, fs=bench.fs, env=env, cwd=bench.repo, timeout=30.0,
                            session=bench._checkout.control.providers)


async def _auth_expiry(bench: Bench) -> Observation:
    stem = "auth-expiry"
    bench.add_ticket(stem, _ticket(stem, "auth.txt", "true"))
    process = _ScriptedProcess([
        lambda _cwd, _env: (1, "", "Invalid API key · Please run /login"),
        lambda _cwd, _env: _claude_result(json.dumps({"verdict": "reject", "lessons": ["re-authenticate"]})),
    ])
    config = _provider_config(bench)
    _use_provider(bench, config.model_copy(update={"caps": config.caps.model_copy(update={"infra": 1})}),
                  process, bench.env)
    await bench.drain()

    terminal = _terminal(bench, stem)
    caps = [event for event in bench.journal.read()
            if event.type == EventType.CAP_CONSUMED and event.ticket == stem
            and event.body.get("cap") == "infra"]
    finding = _finding(bench, stem, "auth_error")
    road = "run claude interactively and complete /login, then uv run python -m chupa drain"
    assert terminal["to"] == "infra_error" and terminal["reason"] == "auth_error"
    assert len(caps) == 1 and finding.paved_road == road
    return Observation("auth_expiry_harvested_with_reauth_road", f"{stem}/0")


async def _planted_secret(bench: Bench) -> Observation:
    stem = "planted-secret"
    secret = "shakeout-secret-4f1ed"
    bench.add_ticket(stem, _ticket(stem, "secret.txt", "test -f secret.txt"))

    async def implement(cwd: Path, env: Mapping[str, str]) -> tuple[int, str, str]:
        assert env["SHAKEOUT_SECRET"] == secret
        (cwd / "secret.txt").write_text("ok\n")
        await process._delegate.run(["git", "add", "secret.txt"], cwd=cwd, env=env, timeout=30.0)
        await process._delegate.run(["git", "commit", "-m", "secret fixture"], cwd=cwd, env=env, timeout=30.0)
        reply = {"outcome": "ok", "summary": f"echoed {secret}", "surprises": secret,
                 "dead_ends": "none", "predicted_vs_actual": "none", "findings": []}
        return _claude_result(json.dumps(reply))

    process = _ScriptedProcess([
        implement,
        lambda _cwd, _env: _claude_result(json.dumps({"verdict": "approve", "summary": "approved", "findings": []})),
    ])
    env = {**bench.env, "SHAKEOUT_SECRET": secret}
    _use_provider(bench, _provider_config(bench, auth="SHAKEOUT_SECRET"), process, env)
    report = await bench.drain()

    record = (bench.repo / "tickets" / stem / "run.md").read_text()
    ticket_files = [path for path in (bench.repo / "tickets").rglob("*") if path.is_file()]
    journal = "\n".join(path.read_text() for path in bench.journal.dir.glob("*.jsonl"))
    assert stem in report.merged and secret not in journal and all(secret not in path.read_text() for path in ticket_files)
    assert "[REDACTED:SHAKEOUT_SECRET]" in record
    return Observation("planted_secret_redacted_from_ticket_plane", f"{stem}/0")


MEMBERS = (
    Member("auth_expiry", "providers", "expired Claude CLI login",
           "auth_expiry_harvested_with_reauth_road", _auth_expiry),
    Member("planted_secret", "providers", "provider auth value echoed by Implement",
           "planted_secret_redacted_from_ticket_plane", _planted_secret),
)
