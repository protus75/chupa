"""Disposable production composition for the shakeout battery."""

import asyncio
import os
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path

from chupa.config import Config, load_config
from chupa.drain import Report, drain
from chupa.git import Git
from chupa.journal import Journal
from chupa.llm import FakeLLM, LLM, ScriptItem
from chupa.runner import Checkout, bind
from chupa.seams import LocalFileSystem, SubprocessExec

_CONFIG = """schema_version: 1
state_dir: .chupa/state
providers:
  - name: fake
    kind: cli
    models_by_tier: {low: fake, medium: fake, high: fake, max: fake}
    limits: {concurrency: 1, est_cost_per_call_usd: 0.0}
routing:
  - {tier: medium, surface: implement, candidates: [{provider: fake}]}
  - {tier: medium, surface: review, candidates: [{provider: fake}]}
review: {}
merge: {}
engine_plane_safety_inventory: [config.yaml]
"""


class AdvancingClock:
    def __init__(self) -> None:
        self.now = datetime(2026, 1, 1, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += timedelta(seconds=seconds)


class Bench:
    def __init__(self, root: Path, llm: LLM | None = None) -> None:
        self.repo = Path(root)
        self.repo.mkdir(parents=True)
        self.fs = LocalFileSystem()
        self.fs.write(self.repo / "config.yaml", _CONFIG.encode())
        self.fs.write(self.repo / ".gitignore", b".chupa/\n")
        self.fs.write(self.repo / "CHUPA_PLAN.md", b"# Shakeout bench\n")
        self.config = load_config(None, cwd=self.repo)
        self.clock = AdvancingClock()
        self.process = SubprocessExec()
        self.env: Mapping[str, str] = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                                        "HOME": str(self.repo), "GIT_CONFIG_NOSYSTEM": "1",
                                        "GIT_AUTHOR_NAME": "shakeout",
                                        "GIT_AUTHOR_EMAIL": "shakeout@example.invalid",
                                        "GIT_COMMITTER_NAME": "shakeout",
                                        "GIT_COMMITTER_EMAIL": "shakeout@example.invalid"}
        self.git = Git(self.process, env=self.env, timeout=30.0)
        self.journal = Journal(self.config.state_dir, self.clock)
        self.llm = llm if llm is not None else FakeLLM([])
        self.report: Report | None = None
        self._initialized = False
        self._checkout = self._compose(self.config)
        self._pipeline = lambda: bind(self._checkout, self.llm)

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.git.init(self.repo, branch="main")
        await self.git.add(self.repo, ["config.yaml", ".gitignore", "CHUPA_PLAN.md"])
        await self.git.commit(self.repo, "bench base")
        self._initialized = True

    def _compose(self, config: Config) -> Checkout:
        return Checkout(repo=self.repo, config=config, env=self.env, exec_=self.process,
                        git=self.git, journal=self.journal, fs=self.fs, clock=self.clock)

    def configure(self, parsed_config: Config) -> None:
        self.config = parsed_config.model_copy(update={"state_dir": self.config.state_dir,
                                                        "worktree_root": self.config.worktree_root})
        self._checkout = self._compose(self.config)
        self._pipeline = lambda: bind(self._checkout, self.llm)

    def add_ticket(self, stem: str, text: str) -> None:
        self.fs.write(self.repo / "tickets" / stem / "ticket.md", text.encode())

    def script(self, items: list[ScriptItem]) -> None:
        if not isinstance(self.llm, FakeLLM):
            raise TypeError("script requires the default FakeLLM")
        self.llm.script.extend(items)

    async def drain(self) -> Report:
        await self.initialize()
        self.report = await drain(self._checkout, self._pipeline(), reexec=SubprocessExec())
        return self.report

    def segments(self):
        return self.journal.read_segments()
