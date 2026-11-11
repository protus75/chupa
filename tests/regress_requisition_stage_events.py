"""Reproduce the missing requisition stage events with a real engine log."""

import asyncio
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from chupa.config import load_config
from chupa.driver import Driver
from chupa.llm import FakeLLM
from chupa.requisition import FIRST_REVIEW, review_ticket

TICKET = """---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- context.txt

## Goal / Why
Create one thing.

## Scope in / Scope out
In: thing. Out: the rest.

## Scope fence
- thing.py

## Acceptance criteria
1. `thing.py` exists, checked by `test -f thing.py`.

## Verification
```
test -f thing.py
```

## Definition of rejected
Needs an outside file.

## Time budget
- expected: 10m
- stuck: 20m
"""
CONFIG = """schema_version: 1
state_dir: .state
providers:
  - name: fake
    kind: cli
    package: test-cli
    auth: FAKE_KEY
    models_by_tier: {low: m, medium: m, high: m, max: m}
    limits: {concurrency: 1, est_cost_per_call_usd: 0.5}
routing:
  - {tier: high, surface: review, candidates: [{provider: fake}]}
review: {}
merge: {}
engine_plane_safety_inventory: [context.txt]
"""


async def never(seconds):
    await asyncio.Event().wait()


with tempfile.TemporaryDirectory() as directory:
    repo = Path(directory)
    (repo / "context.txt").write_text("context")
    (repo / "config.yaml").write_text(CONFIG)
    llm = FakeLLM([json.dumps({"verdict": "approve", "summary": "reviewed", "findings": []})])
    driver = Driver.from_config(load_config(None, cwd=repo), llm=llm, env={"FAKE_KEY": "secret"}, clock=lambda: datetime(2026, 10, 6, tzinfo=UTC), sleep=never)
    asyncio.run(
        review_ticket(
            driver,
            repo=repo,
            stem="one-thing",
            text=TICKET,
            specs_dir=Path(__file__).resolve().parents[1] / "chupa/specs",
            coverage_map=None,
            tier="high",
            stem_slot="slot",
            run_seq=4,
            attempt=2,
            call_seq=1,
            expected_budget="surface",
            prior=FIRST_REVIEW,
        )
    )
    log = repo / ".state/engine.log"
    events = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    stages = [e for e in events if e.get("surface") == "requisition_review" and e["event"] in ("stage_start", "stage_end")]
    passed = [(e["event"], e["stem"], e["attempt"], e["run_seq"]) for e in stages] == [("stage_start", "slot", 2, 4), ("stage_end", "slot", 2, 4)] and stages[-1]["outcome"] == "ok"
    print(json.dumps({"regression_result": "pass" if passed else "defect"}))
    raise SystemExit(0 if passed else 1)
