"""Guard unit-test phases against process and network IO and enforce their budget."""

import os
import socket
import subprocess
import time
from contextlib import ExitStack
from unittest.mock import patch

import pytest

from chupa.covgate import GateInvalid, parse_gate


class UnitIOBlocked(RuntimeError):
    """A unit test attempted process or network IO."""


clock = time.monotonic
_budget = 60
_start = 0
_durations = {}


def _block(name, seam):
    def blocked(*args, **kwargs):
        raise UnitIOBlocked(
            f"{name} is blocked in unit tests; inject the {seam} seam (or a fake) "
            "instead, or move the test to the integration suite"
        )
    return blocked


@pytest.hookimpl(wrapper=True)
def pytest_runtest_setup(item):
    with _guards():
        return (yield)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    with _guards():
        return (yield)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_teardown(item, nextitem):
    with _guards():
        return (yield)


def _guards():
    stack = ExitStack()
    for obj, name, label, seam in (
        (subprocess.Popen, "_execute_child", "subprocess.Popen._execute_child", "process-exec"),
        (os, "system", "os.system", "process-exec"),
        (os, "posix_spawn", "os.posix_spawn", "process-exec"),
        (os, "posix_spawnp", "os.posix_spawnp", "process-exec"),
        (socket.socket, "connect", "socket.socket.connect", "network"),
        (socket.socket, "connect_ex", "socket.socket.connect_ex", "network"),
        (socket.socket, "bind", "socket.socket.bind", "network"),
        (socket, "getaddrinfo", "socket.getaddrinfo", "network"),
    ):
        stack.enter_context(patch.object(obj, name, _block(label, seam)))
    return stack


def pytest_configure(config):
    global _budget
    _durations.clear()
    path = config.rootpath / "test-gate.toml"
    try:
        _budget = parse_gate(path.read_text()).budget_seconds if path.exists() else 60
    except GateInvalid as exc:
        raise pytest.UsageError(f"{path}: {exc.key}: {exc}") from exc


def pytest_sessionstart(session):
    global _start
    _start = clock()


def pytest_runtest_logreport(report):
    _durations[report.nodeid] = _durations.get(report.nodeid, 0) + report.duration


def pytest_sessionfinish(session, exitstatus):
    if hasattr(session.config, "workerinput"):
        return
    elapsed = clock() - _start
    if elapsed > _budget:
        terminal = session.config.pluginmanager.get_plugin("terminalreporter")
        if terminal:
            terminal.write_sep("=", f"Unit suite took {elapsed:.2f}s; budget {_budget}s")
            for nodeid, duration in sorted(_durations.items(), key=lambda item: item[1], reverse=True)[:10]:
                terminal.write_line(f"{nodeid}: {duration:.3f}s")
            terminal.write_line("Speed the listed tests by faking IO and the clock; when no single test dominates, run the unit suite with -n auto.")
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
