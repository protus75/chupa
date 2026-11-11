"""Carried reproducer for signals that terminate a drain without a kill."""

import asyncio
import contextlib
import io
import json
import sys
import tempfile
import traceback
from pathlib import Path


def main():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from chupa import __main__ as cli
        from chupa import runner
        from chupa.llm import FakeLLM
        from tests.integration.test_cli import ENV
        from tests.integration.test_drain import Clock, commit_ticket, confirmed, make_root
        from tests.integration.test_stages import agent

        temporary = tempfile.TemporaryDirectory()
        root = make_root(Path(temporary.name))
        commit_ticket(root, "work", confirmed())
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"regression_result": "error"}))
        return 2

    callbacks = []
    name = "_engine_signals" if hasattr(cli, "_engine_signals") else "_serve" + "_signals"
    setattr(cli, name, lambda cb: (callbacks.append(cb), lambda: None)[1])

    class Blocking(FakeLLM):
        async def call(self, req):
            if callbacks:
                callbacks[0]()
                await asyncio.Event().wait()
            return await super().call(req)

    with contextlib.redirect_stdout(io.StringIO()):
        cli.main(["drain"], cwd=root, env=ENV, clock=Clock(), pipeline=lambda c: runner.bind(c, Blocking([agent({}, outcome="already_satisfied")])))
    events = [json.loads(line) for line in (root / ".chupa/state/engine.log").read_text().splitlines()]
    passed = bool(callbacks) and any(e["event"] == "engine_stop" and e["verb"] == "drain" and e["outcome"] == "killed" for e in events)
    temporary.cleanup()
    print(json.dumps({"regression_result": "pass" if passed else "defect"}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
