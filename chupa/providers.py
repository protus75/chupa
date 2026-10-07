"""Provider layer (CHUPA_PLAN.md section 6): registry + routing, key-scoped child env, the cli adapters.

Routing resolves (tier, surface) to the FIRST candidate only; failover is Phase 4. `CliAdapter` is the
shared base and the trust boundary -- write-grant derivation, redaction of both sinks (the captured
stream and the returned result), and the cost floor live there ONCE; each subclass is only its CLI's
argv contract and event-stream parse.
"""

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from chupa.config import Config, ConfigSnapshot, Provider
from chupa.llm import AgentEffort, AgentTier, LLMRequest, LLMResult
from chupa.redact import Redactor
from chupa.seams import FileSystem, GroupExec

# Closed allowlist of tree-writing surfaces: every other surface is called read-only.
WRITING_SURFACES = frozenset({"implement"})

# Section 0: the value prompt 1 authors when the operator stated none; it must never reach a model.
PLACEHOLDER = "OPERATOR-SETS-THIS"

FailureClass = Literal["rate_limited", "quota_exhausted", "outage", "auth_error", "model_error", "unclassified"]

FAILURE_MARKERS: tuple[tuple[FailureClass, tuple[str, ...]], ...] = (
    ("quota_exhausted", ("quota exhausted", "usage limit reached", "out of extra usage")),
    ("rate_limited", ("rate limit", "too many requests")),
    ("outage", ("service unavailable", "internal server error", "stream disconnected", "at capacity")),
    ("model_error", ("model unavailable", "model not found", "model is not supported")),
)


class ProviderSetupError(Exception):
    """A config/setup refusal raised before any call runs: nothing was metered."""


class ProviderCallError(Exception):
    """The CLI ran and failed. `stderr_tail` is scrubbed."""

    def __init__(
        self,
        provider: str,
        message: str,
        *,
        rc: int,
        stderr_tail: str,
        failure_class: str | None = None,
        paved_road: str | None = None,
    ) -> None:
        super().__init__(f"{provider}: {message} (exit {rc}); stderr tail: {stderr_tail!r}")
        self.provider = provider
        self.rc = rc
        self.stderr_tail = stderr_tail
        self.failure_class = failure_class
        self.paved_road = paved_road


def secret_names(config: Config | ConfigSnapshot) -> frozenset[str]:
    return frozenset(p.auth for p in config.providers if p.auth)


def child_env(
    env: Mapping[str, str], config: Config | ConfigSnapshot,
    serving: Provider | ConfigSnapshot | None = None,
) -> dict[str, str]:
    """INHERIT-MINUS-SECRETS: the full parent env minus every provider key, plus only the serving call's own.

    Every non-LLM child (checks, verification, replay) passes `serving=None` and gets no key at all.
    """
    out = {k: v for k, v in env.items() if k not in secret_names(config)}
    if serving is not None and serving.auth:
        if serving.auth not in env:
            raise ProviderSetupError(
                f"provider {serving.name!r} needs env var {serving.auth} and it is unset; export it before the run"
            )
        out[serving.auth] = env[serving.auth]
    return out


@dataclass(frozen=True)
class Served:
    provider: Provider | ConfigSnapshot
    model: str


def resolve(config: Config | ConfigSnapshot, tier: AgentTier, surface: str) -> Served:
    """The FIRST candidate of the (tier, surface) row; its model, else the provider's models_by_tier[tier]."""
    route = next((r for r in config.routing if r.tier == tier and r.surface == surface), None)
    if route is None and surface != "review":
        route = next((r for r in config.routing if r.tier == tier and r.surface == "review"), None)
    if route is None:
        raise ProviderSetupError(
            f"no routing row for tier {tier!r}, surface {surface!r}; add one under `routing:` in config.yaml"
        )
    cand = route.candidates[0]
    provider = next(p for p in config.providers if p.name == cand.provider)  # load_config checked the reference
    model = cand.model if cand.model is not None else getattr(provider.models_by_tier, tier)
    if PLACEHOLDER in (model, provider.auth):
        raise ProviderSetupError(
            f"routing for tier {tier!r}, surface {surface!r} resolves to provider {provider.name!r} still carrying"
            f" {PLACEHOLDER}; set the operator values in config.yaml (Phase 1 prerequisites, section 0)"
        )
    return Served(provider, model)


@dataclass(frozen=True)
class Parsed:
    text: str
    input_tokens: int | None
    output_tokens: int | None
    usd: float | None  # None: the stream reports no cost, so the declared estimate charges


class CliAdapter:
    """Shared base for one agent CLI. Subclasses supply `binary`, `reports_cost`, `argv`, `parse`."""

    binary: str
    reports_cost: bool
    AUTH_MARKERS: tuple[str, ...]
    LOGIN_ROAD: str

    def __init__(
        self,
        provider: Provider | ConfigSnapshot,
        *,
        config: Config | ConfigSnapshot,
        exec_: GroupExec,
        fs: FileSystem,
        redactor: Redactor,
        env: Mapping[str, str],
        cwd: Path,
        capture_dir: Path,
        timeout: float,
    ) -> None:
        if not self.reports_cost and provider.limits.est_cost_per_call_usd is None:
            raise ProviderSetupError(
                f"provider {provider.name!r}: the {self.binary} stream reports no cost, so"
                f" limits.est_cost_per_call_usd is required; declare a flat per-call estimate"
            )
        self.provider = provider
        self._config = config
        self._exec = exec_
        self._fs = fs
        self._redactor = redactor
        self._env = env
        self._cwd = cwd
        self._capture_dir = capture_dir
        self._timeout = timeout
        self._seq = 0
        self._pgid: int | None = None

    def argv(self, model: str, effort: AgentEffort, writes: bool) -> list[str]:
        raise NotImplementedError

    def parse(self, out: str) -> Parsed:
        """Raise `ValueError` naming the failure when the stream carries no successful result."""
        raise NotImplementedError

    async def invoke(self, req: LLMRequest, model: str) -> LLMResult:
        writes = req.surface in WRITING_SURFACES
        if writes and req.worktree is None:
            raise ProviderSetupError(f"surface {req.surface!r} writes the tree but the request carries no worktree")
        self._seq += 1
        call_dir = self._capture_dir / (req.ticket or req.surface) / f"{self.provider.name}-{self._seq:04d}"
        prompt = call_dir / "prompt.md"
        # The prompt reaches the CLI only as a file on stdin: an argv element is capped by the OS limit.
        self._fs.write(prompt, self._redactor.scrub(req.rendered).encode())
        try:
            rc, out, err = await self._exec.run(
                self.argv(model, req.effort, writes),
                cwd=req.worktree if writes else self._cwd,
                env=child_env(self._env, self._config, self.provider),
                timeout=self._timeout,
                stdin_path=prompt,
                on_spawn=self._spawned,
            )
        finally:
            self._pgid = None
        out, err = self._redactor.scrub(out), self._redactor.scrub(err)
        self._fs.write(call_dir / "events.jsonl", out.encode())
        self._fs.write(call_dir / "stderr.txt", err.encode())
        tail = err[-2000:]
        if rc != 0:
            # A CLI may report its failure in the event stream, not stderr: carry that message forward.
            try:
                self.parse(out)
                message = "nonzero exit"
            except ValueError as e:
                message = f"nonzero exit: {e}"
            self._raise_call_error(message, rc=rc, stderr_tail=tail)
        try:
            parsed = self.parse(out)
        except ValueError as e:
            self._raise_call_error(str(e), rc=rc, stderr_tail=tail)
        usd = parsed.usd if parsed.usd is not None else self.provider.limits.est_cost_per_call_usd
        if usd is None:
            self._raise_call_error(
                "stream reported no cost and limits.est_cost_per_call_usd is unset; declare the estimate",
                rc=rc,
                stderr_tail=tail,
            )
        return LLMResult(
            # Scrubbed BEFORE it becomes the result: the one version that ever exists. Again after
            # decoding, since a JSON-escaped secret survives the raw-stream scrub.
            text=self._redactor.scrub(parsed.text),
            input_tokens=parsed.input_tokens,
            output_tokens=parsed.output_tokens,
            provider=self.provider.name,
            model=model,
            usd=usd,
        )

    def _spawned(self, pgid: int) -> None:
        self._pgid = pgid

    def classify_failure(self, message: str, *, rc: int, stderr_tail: str) -> ProviderCallError:
        """Dormant Phase 3 classifier: only failed diagnostics, never successful output."""
        message = self._redactor.scrub(message)
        tail = stderr_tail[-2000:]
        diagnostic = f"{tail}\n{message}".lower()
        markers = (("auth_error", self.AUTH_MARKERS), *FAILURE_MARKERS)
        failure = next((kind for kind, words in markers if any(w in diagnostic for w in words)), "unclassified")
        road = None
        if failure == "auth_error":
            road = self.LOGIN_ROAD
        elif failure == "model_error":
            road = f"fix provider {self.provider.name!r}'s model route in config.yaml, then retry"
        elif failure != "unclassified":
            road = f"wait for provider {self.provider.name!r} to recover from {failure}, then retry"
        return ProviderCallError(self.provider.name, message, rc=rc, stderr_tail=tail,
                                 failure_class=failure, paved_road=road)

    def parsed_failure(self, out: str, *, rc: int, stderr_tail: str) -> ProviderCallError | None:
        """Direct construction seam; invoke retains its existing production error handling."""
        try:
            self.parse(out)
        except ValueError as exc:
            return self.classify_failure(str(exc), rc=rc, stderr_tail=stderr_tail)
        if rc != 0:
            return self.classify_failure("nonzero exit", rc=rc, stderr_tail=stderr_tail)
        return None

    def _raise_call_error(self, message: str, *, rc: int, stderr_tail: str) -> None:
        auth = any(marker in f"{stderr_tail}\n{message}".lower() for marker in self.AUTH_MARKERS)
        raise ProviderCallError(
            self.provider.name,
            message,
            rc=rc,
            stderr_tail=stderr_tail,
            failure_class="auth_error" if auth else None,
            paved_road=self.LOGIN_ROAD if auth else None,
        )

    def abort(self) -> None:
        if self._pgid is not None:
            self._exec.kill_group(self._pgid)


def _events(out: str) -> list[dict]:
    # Non-JSON lines (a CLI warning on stdout) stay in the capture; success still requires the terminal event.
    events = []
    for line in out.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


class ClaudeAdapter(CliAdapter):
    binary = "claude"
    reports_cost = True
    AUTH_MARKERS = ("invalid api key", "please run /login", "not logged in", "oauth token has expired")
    LOGIN_ROAD = "run claude interactively and complete /login, then uv run python -m chupa drain"

    def argv(self, model: str, effort: AgentEffort, writes: bool) -> list[str]:
        # No effort flag: effort is recorded in provenance only. stream-json under -p requires --verbose.
        grant = ["--permission-mode", "bypassPermissions"] if writes else ["--allowedTools", "Read", "Grep", "Glob", "LS"]
        return [self.binary, "-p", "--output-format", "stream-json", "--verbose", "--model", model, *grant]

    def parse(self, out: str) -> Parsed:
        result = next((e for e in reversed(_events(out)) if e.get("type") == "result"), None)
        if result is None:
            raise ValueError("no terminal `result` event in the stream")
        if result.get("is_error") or result.get("subtype") != "success":
            raise ValueError(f"result event reports failure: {result.get('subtype')}: {result.get('result')!r}")
        usage = result.get("usage") or {}
        inputs = [usage.get(k) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")]
        known = [n for n in inputs if isinstance(n, int)]
        return Parsed(
            text=str(result.get("result", "")),
            input_tokens=sum(known) if known else None,
            output_tokens=usage.get("output_tokens"),
            usd=result.get("total_cost_usd"),
        )


class CodexAdapter(CliAdapter):
    binary = "codex"
    reports_cost = False
    AUTH_MARKERS = ("not logged in", "401 unauthorized", "token has expired")
    LOGIN_ROAD = "run codex login, then uv run python -m chupa drain"

    def argv(self, model: str, effort: AgentEffort, writes: bool) -> list[str]:
        grant = (
            ["--dangerously-bypass-approvals-and-sandbox"]
            if writes
            else ["--sandbox", "read-only", "-c", "approval_policy=never"]
        )
        # Trailing `-`: the prompt is read from stdin.
        return [self.binary, "exec", "--json", "-m", model, "-c", f"model_reasoning_effort={effort}", *grant, "-"]

    def parse(self, out: str) -> Parsed:
        text = None
        input_tokens = output_tokens = None
        for e in _events(out):
            kind = e.get("type")
            # codex exits 0 on a failed turn: these events, not the exit code, are the failure signal.
            if kind == "turn.failed":
                raise ValueError(f"turn.failed: {(e.get('error') or {}).get('message')!r}")
            if kind == "error":
                raise ValueError(f"error event: {e.get('message')!r}")
            item = e.get("item") or {}
            if kind == "item.completed" and item.get("type") == "agent_message":
                text = str(item.get("text", ""))
            if kind == "turn.completed":
                usage = e.get("usage") or {}
                input_tokens, output_tokens = usage.get("input_tokens"), usage.get("output_tokens")
        if text is None:
            raise ValueError("no `agent_message` item in the stream")
        return Parsed(text=text, input_tokens=input_tokens, output_tokens=output_tokens, usd=None)


ADAPTERS: dict[str, type[CliAdapter]] = {"claude": ClaudeAdapter, "codex": CodexAdapter}


PROBE_PROMPT = "Reply with the single word ok."
PREFLIGHT_TIMEOUT_S = 120.0


class ProviderLLM:
    """The real `LLM`: one adapter per configured provider, each call served by its route's first candidate."""

    kind: Literal["api", "cli"] = "cli"

    def __init__(
        self,
        config: Config | ConfigSnapshot,
        *,
        exec_: GroupExec,
        fs: FileSystem,
        env: Mapping[str, str],
        cwd: Path,
        timeout: float,
    ) -> None:
        self._config = config
        self._exec, self._env, self._cwd = exec_, env, cwd
        redactor = Redactor.from_config(config, env)
        self._adapters: dict[str, CliAdapter] = {}
        for p in config.providers:
            if p.name not in ADAPTERS:
                raise ProviderSetupError(
                    f"provider {p.name!r} has no shipped cli adapter; name a provider one of {sorted(ADAPTERS)}"
                )
            self._adapters[p.name] = ADAPTERS[p.name](
                p,
                config=config,
                exec_=exec_,
                fs=fs,
                redactor=redactor,
                env=env,
                cwd=cwd,
                capture_dir=config.state_dir / "spools" / "providers",
                timeout=timeout,
            )
        self._active: CliAdapter | None = None

    async def preflight(self) -> list[str]:
        """Section 6.11: every cli provider at its latest pnpm release, every routed (provider, model) answering.

        Returns each refusal reason with its paved road; empty means the run may dispatch.
        """
        problems: list[str] = []
        for adapter in self._adapters.values():
            package = adapter.provider.package
            _, out, err = await self._exec.run([adapter.binary, "--version"], cwd=self._cwd, env=self._env,
                                               timeout=PREFLIGHT_TIMEOUT_S)
            _, latest, _ = await self._exec.run(["pnpm", "view", str(package), "version"], cwd=self._cwd,
                                                env=self._env, timeout=PREFLIGHT_TIMEOUT_S)
            installed = re.search(r"\d+\.\d+\.\d+", out + err)
            if not latest.strip() or installed is None or installed.group(0) != latest.strip():
                problems.append(f"{adapter.binary} {installed.group(0) if installed else '(unknown)'} is not the"
                                f" latest release {latest.strip() or '(unreadable)'} -- run: pnpm add -g {package}@latest")
        probed: set[tuple[str, str]] = set()
        for route in self._config.routing:
            for cand in route.candidates:
                adapter = self._adapters[cand.provider]
                model = cand.model or getattr(adapter.provider.models_by_tier, route.tier)
                if (cand.provider, model) in probed:
                    continue
                probed.add((cand.provider, model))
                req = LLMRequest(surface="preflight", rendered=PROBE_PROMPT, tier=route.tier, effort="low",
                                 ticket=None, worktree=None)
                try:
                    await adapter.invoke(req, model)
                except Exception as e:
                    problems.append(f"{cand.provider} model {model!r} failed its probe: {e} -- install the latest"
                                    f" {adapter.binary} or route a model this login serves in config.yaml")
        return problems

    async def call(self, req: LLMRequest) -> LLMResult:
        served = resolve(self._config, req.tier, req.surface)
        self._active = self._adapters[served.provider.name]
        try:
            return await self._active.invoke(req, served.model)
        finally:
            self._active = None

    def abort_current(self) -> None:
        if self._active is not None:
            self._active.abort()
