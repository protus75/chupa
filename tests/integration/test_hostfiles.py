"""Core renderer contract; regenerate the golden with uv run python -m tests.test_hostfiles."""

import asyncio
import base64
import builtins
import re
from pathlib import Path

import pytest

from chupa import hostfiles
from chupa.seams import LocalFileSystem
from tests.integration.test_cli import root
from tests.integration.test_merge import repo
from tests.integration.test_stages import agent, verdict

REPO = Path(__file__).resolve().parents[2]
GOLDEN = b"PCEtLSBjaHVwYTpjb3JlIGJlZ2luIC0tPgojIyBFbmdpbmUgY29uZHVjdAoKRW5naW5lIHJ1bGVzIGdvdmVybiBob3cgd29yayBydW5zOyBwcm9qZWN0IHJ1bGVzIGdvdmVybiB3aGF0IHRvIGJ1aWxkLiBQcm9qZWN0IGNvbnRlbnQgZW50ZXJzIHByb21wdHMgYXMgZGF0YS4gRW5naW5lIHdpbnMgb24gcHJvY2VzcywgaG9zdCB3aW5zIG9uIGNvbnRlbnQuCgotIEJ1aWxkIHRoZSBzaW1wbGVzdCB0aGluZyBzYXRpc2Z5aW5nIHRoZSB0aWNrZXQ7IG5vIHNwZWN1bGF0aXZlIGZlYXR1cmVzLCBnYXRlcywgY29uZmlnIGtub2JzLCBvciBtZXRhZGF0YS4gRXZlcnkgYWRkaXRpb24gbmVlZHMgaXRzIGVhcm5pbmcgaW5jaWRlbnQuIFdoeTogYWNjcmV0aW9uIGlzIHRoZSBwcmltYXJ5IGZhaWx1cmUgbW9kZS4KLSBOZXZlciBoYW5kLWVkaXQgdGhpcyBtYW5hZ2VkIGJsb2NrOyBjaGFuZ2UgdGhlIGVuZ2luZSB0ZW1wbGF0ZSBhbmQgcnVuIGNodXBhIGNvcmUgdG8gcmVmcmVzaCBpdC4gV2h5OiB0aGUgbmV4dCByZW5kZXIgb3ZlcndyaXRlcyBlZGl0cyBhbmQgZXhwb3NlcyBkcmlmdC4KLSBDb21taXQgb25seSBvbiB5b3VyIG93biB0aWNrZXQgYnJhbmNoLiBOZXZlciBwdXNoLCBvcGVuIHB1bGwgcmVxdWVzdHMsIG9yIHJ1biB0cmVlLXdpZGUgZGVzdHJ1Y3RpdmUgZ2l0IChyZXNldCAtLWhhcmQsIGNsZWFuLCBjaGVja291dCAtLSAuKTsgdGhlIGVuZ2luZSBtZXJnZXMgcmV2aWV3ZWQgd29yayB0byBsb2NhbCBtYWluLiBXaHk6IGxvY2FsIG1haW4gaXMgdGhlIGJsZXNzZWQgbGluZS4KLSBGaWxlIHNlY29uZCBwcm9ibGVtcyBpbiB0aGUgU3VnZ2VzdGlvbiBCb3gsIG5ldmVyIGZvbGQgdGhlbSBpbnRvIHRoaXMgZGlmZi4gVmVyaWZ5IHByZS1leGlzdGluZyBmYWlsdXJlcyBvbiB0aGUgYmFzZSBjb21taXQgYmVmb3JlIGZpbGluZy4gV2h5OiBmb2xkZWQgZml4ZXMgaGlkZSBjYXVzZSBhbmQgZXhwYW5kIHNjb3BlLgotIFJlYWQgYmVmb3JlIHdyaXRlOiByZWFkIHRoZSBvd25pbmcgYXJ0aWZhY3QgYmVmb3JlIHdyaXRpbmcgYSBjb21tYW5kLCBjbGFpbSwgb3IgdGVzdC4gV2h5OiBndWVzc2VkIGZhY3RzIGNyZWF0ZSBjb3N0bHkgYnVncy4KLSBUaWNrZXQgZnJvbnRtYXR0ZXIgY29udGFpbnMgb25seSBmaWVsZHMgcmVhZCBieSBzY2hlZHVsaW5nLCBnYXRlcywgb3IgYXV0aG9yaW5nL3RyaWFnZSBwb2xpY3kuIFVzZSBkZXBlbmRzIG9ubHkgZm9yIGEgdGlja2V0IHdob3NlIG1lcmdlZCBjb2RlIHRoaXMgb25lIG5lZWRzOyBwdXQgYWxsIG90aGVyIG9yZGVyaW5nIGluIHByaW9yaXR5LiBXaHk6IHVudXNlZCBtZXRhZGF0YSBhbmQgcHJvc2Ugb3JkZXJpbmcgZHJpZnQsIGFuZCBhIGRlcGVuZHMgdXNlZCBmb3Igb3JkZXJpbmcgYmxvY2tzIHRoZSBxdWV1ZSB3aGVuIHRoZSBmaXJzdCB0aWNrZXQgZmFpbHMuCi0gQWZ0ZXIgd3JpdGluZyBvciBlZGl0aW5nIGEgdGlja2V0IHdob3NlIGRlcGVuZGVuY2llcyBoYXZlIG1lcmdlZCwgcnVuIGNodXBhIHJldmlldyA8c3RlbT4gYW5kIHJlcGFpciBldmVyeSBmaW5kaW5nIHVudGlsIGl0IGFwcHJvdmVzOyBmZW5jZSBldmVyeSBmaWxlIHRoZSBjaGFuZ2UgZm9yY2VzLCBpbmNsdWRpbmcgY2FsbGVycywgaW1wb3J0ZXJzLCBhbmQgdGVzdHMgdGhhdCBwaW4gYSBjaGFuZ2VkIG5hbWUsIHZhbHVlLCBvciB2ZXJzaW9uLiBXaHk6IGEgZm9yY2VkIGZpbGUgb3V0c2lkZSB0aGUgZmVuY2UgbWFrZXMgdGhlIHRpY2tldCBpbXBvc3NpYmxlLgoKIyMgQ2hhdCBzZXNzaW9uIGNvbmR1Y3QKClRoZXNlIHJ1bGVzIGdvdmVybiBJTlRFUkFDVElWRSBDSEFUIFNFU1NJT05TIHdpdGggdGhlIG93bmVyIHByZXNlbnQuIFRpY2tldCBhZ2VudHMgcnVubmluZyB1bmRlcgpjaHVwYSBza2lwIHRoaXMgc2VjdGlvbjsgYSBjb25maXJtZWQgdGlja2V0IGlzIHRoZSBhcHByb3ZhbCBmb3IgaXRzIG93biBzY29wZS4KCiMjIyBDUklUSUNBTDogQWx3YXlzIHByb3Bvc2UgYSB0aWNrZXQgLS0gbmV2ZXIgaGFuZC1lZGl0IG1haW4gZnJvbSBjaGF0CgoqKkhBUkQgUlVMRSAtLSBubyBleGNlcHRpb25zLioqIFdoZW4gdGhlIHVzZXIgYXNrcyBmb3IgQU5ZIGNoYW5nZSB0byByZXBvCmNvbnRlbnQgZnJvbSBhIGNoYXQgc2Vzc2lvbiAtLSBjb2RlLCBkb2NzLCBDTEFVREUubWQsIEFHRU5UUy5tZCwKYC5jbGF1ZGUvc2V0dGluZ3MuanNvbmAsIGhvb2tzLCBzY3JpcHRzLCBwcm9qZWN0IGNvbmZpZywgYWdlbnQgcnVsZXMsIG9yCmFueXRoaW5nIHRyYWNrZWQgaW4gZ2l0IG91dHNpZGUgdGhlIHRpY2tldC1tYWludGVuYW5jZSBjYXJ2ZS1vdXQgYmVsb3cgLS0geW91cgpkZWZhdWx0IGFuZCBuZWFyLW9ubHkgcmVzcG9uc2UgaXMgdG8gKipkcmFmdCBhIHRpY2tldCBmaWxlIGF0CmB0aWNrZXRzLzxzdGVtPi90aWNrZXQubWRgKiogZm9sbG93aW5nIGBjaHVwYSBuZXdgLCBgY2h1cGEgbGludGAsIGFuZApgY2h1cGEgcmV2aWV3YCwgYW5kIHN0b3AuIERvIG5vdCBlZGl0IG9yIGNvbW1pdCBkaXJlY3RseSBvbiBgbWFpbmAuCgpUaGUgb25seSB0aW1lcyB5b3UgbWF5IGVkaXQgYG1haW5gIGRpcmVjdGx5IGZyb20gY2hhdCBhcmU6CgoxLiBUaGUgdXNlciBleHBsaWNpdGx5IHNheXMgImVkaXQgbWFpbiIsICJjb21taXQgZGlyZWN0bHkiLCAic2tpcCB0aGUKICAgdGlja2V0IiwgImRvIGl0IGlubGluZSIsIG9yIGVxdWl2YWxlbnRseSB1bmFtYmlndW91cyBvdmVycmlkZSBpbiB0aGUKICAgc2FtZSB0dXJuLiBBbmdlciB3b3JkcyBhbG9uZSBkbyBub3QgY291bnQuCjIuIFlvdSBhcmUgaW5zaWRlIGFuIGFjdGl2ZSBjaHVwYSB0aWNrZXQgd29ya3RyZWUsIGluIHdoaWNoIGNhc2UgdGhlIHRpY2tldAogICB3b3JrZmxvdydzIG93biBydWxlcyBhcHBseS4KMy4gSW4gYW4gaW50ZXJhY3RpdmUgaHVtYW4gY2hhdCBzZXNzaW9uIGluIHRoZSBob3N0IGNoZWNrb3V0LCB0aGUgdXNlcgogICBkaXJlY3RzIHlvdSBieSBleHBsaWNpdCBwYXRoIHRvIGVkaXQgb3IgZGVsZXRlIGFuIGV4aXN0aW5nIHRpY2tldCBmaWxlIHVuZGVyCiAgIGB0aWNrZXRzL2Agb3IgYW55IG90aGVyIGZpbGUgaW4gdGhhdCB0aWNrZXQncyBgdGlja2V0cy88c3RlbT4vYCBkaXJlY3RvcnkuCiAgIERlbGV0aW5nIG9uZSBvZiB0aG9zZSBmaWxlcyBvbiBpdHMgb3duIGlzIGluY2x1ZGVkLiBUaGlzIGlzIHRpY2tldAogICBtYWludGVuYW5jZSBhbmQgZG9lcyBub3QgcmVxdWlyZSBkcmFmdGluZyBhIHRpY2tldC1hYm91dC1hLXRpY2tldCBmaXJzdC4KNC4gUmVhZC1vbmx5IGluc3BlY3Rpb24gKGdyZXAsIGdpdCBzdGF0dXMsIGdpdCBkaWZmLCBnaXQgbG9nLCBnaCBwciB2aWV3KSAtLQogICBuZXZlciBhIHdyaXRlLgo1LiBTdXBlcnZpc2luZyBzZXNzaW9uLiBBIHNlc3Npb24gbWF5LCB1bmFza2VkLCBmaXggYSB0aWNrZXQncyBsaW50IG9yIGZvcm1hdAogICBlcnJvcnMsIGFkZCBhIGZpbGUgbWlzc2luZyBmcm9tIGl0cyBgIyMgU2NvcGUgZmVuY2VgIG9yIGAjIyBDb250ZXh0YCwgY29ycmVjdAogICBhIHN0YWxlIHBhdGgsIG1ha2UgYSBzaW1wbGUgd29yZGluZyB1cGRhdGUsIGFuZCBydW4gb3IgcmVzdGFydCB0aGUgZHJhaW4uCiAgIEEgc2Vzc2lvbiBtYXkgbm90IHJ1biBgY29uZmlybWAgb3IgYHJlamVjdGAsIHJldHJ5IG9yIHJlLWZlZWQgYSBzdGVtIHdob3NlCiAgIGNhcHMgYXJlIHNwZW50LCBlZGl0IGEgcnVubmluZyB0aWNrZXQsIGNoYW5nZSBhIHRpY2tldCdzIGdvYWwgb3Igc2NvcGUsIG9yCiAgIGhhbmQtcmV3cml0ZSBhIHRpY2tldCB0aGUgZW5naW5lIGF1dGhvcmVkLiBUaG9zZSBkZWNpc2lvbnMgZ28gdG8gdGhlIHVzZXIuCiAgIFdoeTogdGhlIHF1ZXVlIGtlZXBzIG1vdmluZyBvbiBvYnZpb3VzIGZpeGVzIHdoaWxlIGV2ZXJ5IGp1ZGdtZW50IGNhbGwgc3RheXMKICAgd2l0aCB0aGUgdXNlci4KCklmIHlvdSBoYXZlIGFscmVhZHkgc3RhcnRlZCBlZGl0aW5nIG9yIGhhdmUgZWRpdGVkIG1haW4gd2l0aG91dCBhbiBleHBsaWNpdApvdmVycmlkZTogc3RvcCBpbW1lZGlhdGVseSwgdGVsbCB0aGUgdXNlciB5b3UgYnJva2UgdGhpcyBydWxlLCBhbmQgYXNrIHdoZXRoZXIKdG8gcmV2ZXJ0IHRoZSBjb21taXQgYW5kIHJlZmlsZSBhcyBhIHRpY2tldC4KCldoeTogZGlyZWN0IGNoYXQgZWRpdHMgYnlwYXNzIHRoZSB0aWNrZXQsIHJ1bi1yZWNvcmQsIHJldmlldywgZGVwZW5kZW5jeSwgYW5kCnJldHJvIGFydGlmYWN0cyB0aGF0IG1ha2UgY2h1cGEgZGVidWdnYWJsZS4KPCEtLSBjaHVwYTpjb3JlIGVuZCAtLT4KCg=="


class RecordingFS(LocalFileSystem):
    def __init__(self):
        self.writes = []

    def write(self, path, data):
        self.writes.append((path, data))
        super().write(path, data)


def test_core_template_is_host_neutral():
    for term in (b"git.py", b"Pure Python", b"seams", b"journal", b"shell=True", b"chupa:core"):
        assert term not in hostfiles.CORE_TEMPLATE
    assert b"## Chat session conduct" in hostfiles.CORE_TEMPLATE
    assert b"### CRITICAL: Always propose a ticket -- never hand-edit main from chat" in hostfiles.CORE_TEMPLATE
    assert b"Anger words alone do not count." in hostfiles.CORE_TEMPLATE
    assert sum(line.startswith(b"- ") for line in hostfiles.CORE_TEMPLATE.splitlines()) == 7
    assert b"Use depends only for a ticket whose merged code this one needs" in hostfiles.CORE_TEMPLATE
    assert b"Put ordering in depends" not in hostfiles.CORE_TEMPLATE


@pytest.mark.parametrize(
    "project",
    [
        None,
        b"",
        b"# Project\n\nrules\n",
        b"one\r\ntwo\nthree\r\nfour",
        b"no final newline\xff",
        hostfiles.parse((REPO / "CLAUDE.md").read_bytes())[1][2:],
        hostfiles.parse((REPO / "AGENTS.md").read_bytes())[1][2:],
    ],
)
def test_core_first_adoption_preserves_project_bytes(tmp_path, project):
    path = tmp_path / "CLAUDE.md"
    if project is not None:
        path.write_bytes(project)
    fs = RecordingFS()
    hostfiles.refresh([path], fs)
    result = path.read_bytes()
    block = hostfiles.BEGIN + b"\n" + hostfiles.CORE_TEMPLATE + hostfiles.END
    assert result == block + b"\n\n" + (project or b"")
    assert fs.writes == [(path, result)]
    assert hostfiles.parse(result) == (b"", b"\n\n" + (project or b""))


@pytest.mark.parametrize("ending", [b"\n", b"\r\n", b"\r"])
@pytest.mark.parametrize("suffix", [b"", b"\n\nproject\r\ntail without newline\xff", b"\r\nlast\n"])
def test_core_refresh_preserves_remainder(tmp_path, ending, suffix):
    prefix = b"# Identity\r\n\nproject prefix\xff\r\n"
    previous = prefix + hostfiles.BEGIN + ending + b"old rules" + ending + hostfiles.END + suffix
    expected = prefix + hostfiles.BEGIN + b"\n" + hostfiles.CORE_TEMPLATE + hostfiles.END + suffix
    assert hostfiles.parse(previous) == (prefix, suffix)
    assert hostfiles.render(previous) == expected
    path = tmp_path / "AGENTS.md"
    path.write_bytes(previous)
    hostfiles.refresh([path], RecordingFS())
    assert path.read_bytes() == expected


CORRUPT = [
    b"<!-- chupa:core begin --> extra\n" + hostfiles.END,
    b"<!-- chupa:core beg",
    hostfiles.BEGIN + b"\nold\n",
    hostfiles.END,
    hostfiles.END + b"\n" + hostfiles.BEGIN,
    hostfiles.BEGIN + b"\n" + hostfiles.BEGIN + b"\n" + hostfiles.END,
    hostfiles.BEGIN + b"\n" + hostfiles.END + b"\n" + hostfiles.END,
    b"inline " + hostfiles.BEGIN + b"\n" + hostfiles.END,
    hostfiles.BEGIN + b"\nstray chupa:core\n" + hostfiles.END,
    hostfiles.BEGIN + b"\nold\n" + hostfiles.END + b"\nstray chupa:core",
    b"stray chupa:core\n" + hostfiles.BEGIN + b"\n" + hostfiles.END,
    b" <!-- chupa:core begin -->\n" + hostfiles.END,
    hostfiles.BEGIN + b"\n<!-- chupa:core end --",
]


@pytest.mark.parametrize("corrupt", CORRUPT)
@pytest.mark.parametrize("first", [None, b"project\r\nkeep me"])
def test_core_marker_corruption_refuses_without_writes(tmp_path, corrupt, first):
    clean, broken = tmp_path / "CLAUDE.md", tmp_path / "AGENTS.md"
    if first is not None:
        clean.write_bytes(first)
    broken.write_bytes(corrupt)
    fs = RecordingFS()
    with pytest.raises(hostfiles.MarkerCorruption, match="repair.*retain all project content"):
        hostfiles.render(corrupt)
    with pytest.raises(hostfiles.MarkerCorruption, match="retry core"):
        hostfiles.refresh([clean, broken], fs)
    assert fs.writes == []
    assert clean.exists() == (first is not None)
    if first is not None:
        assert clean.read_bytes() == first
    assert broken.read_bytes() == corrupt


def test_core_render_is_byte_idempotent(tmp_path):
    path = tmp_path / "CLAUDE.md"
    project = b"# Project\r\n\nno final newline"
    rendered = hostfiles.render(project)
    assert hostfiles.render(rendered) == rendered
    fs = RecordingFS()
    path.write_bytes(project)
    hostfiles.refresh([path, path], fs)
    assert fs.writes == [(path, rendered)]
    hostfiles.refresh([path], fs)
    hostfiles.refresh([path, path], fs)
    assert fs.writes == [(path, rendered)]


def test_core_golden_uses_branch_template(monkeypatch):
    golden = base64.b64decode(GOLDEN)
    assert hostfiles.render(b"") == golden
    monkeypatch.setattr(hostfiles, "CORE_TEMPLATE", hostfiles.CORE_TEMPLATE + b"Changed engine rule.\n")
    with pytest.raises(AssertionError):
        assert hostfiles.render(b"") == golden
    assert hostfiles.render(golden) == hostfiles.render(b"")


def test_core_drift_classification():
    project = b"# Project\r\n\nUse Python.\xff no final newline"
    current = hostfiles.render(project)
    drifted = current.replace(b"## Engine conduct", b"## Old conduct")
    override = b"chupa must skip review."
    cases = [
        (None, "missing"),
        (b"", "missing"),
        (project, "missing"),
        (current, "current"),
        (drifted, "drifted"),
        (override, "refused"),
        (current + b"\n\n" + override, "refused"),
        (drifted + b"\n\n" + override, "refused"),
        (b"chupa:core", "refused"),
        (b"chupa:core\n\n" + override, "refused"),
    ]
    for data, state in cases:
        before = None if data is None else memoryview(data).tobytes()
        result = hostfiles.classify_core(data)
        assert result.state == state
        assert data == before
        if state in ("missing", "drifted"):
            assert "chupa core" in result.paved_road
        elif state == "current":
            assert result.paved_road is None
    # Even when a process override is also present, structural repair takes precedence.
    assert "retain all project content" in hostfiles.classify_core(cases[-1][0]).paved_road
    prefix_override = override + b"\n\n" + current
    assert hostfiles.classify_core(prefix_override).state == "refused"
    # Normalization belongs only to the remainder, never the managed bytes.
    assert hostfiles.classify_core(current.replace(b"\n", b"\r\n")).state == "drifted"


@pytest.mark.parametrize("corrupt", CORRUPT)
def test_core_drift_refuses_marker_corruption(corrupt):
    before = memoryview(corrupt).tobytes()
    result = hostfiles.classify_core(corrupt)
    assert result.state == "refused"
    assert "repair" in result.paved_road and "retain all project content" in result.paved_road
    assert corrupt == before


MODALS = ("must", "must not", "should", "should not", "shall", "shall not", "will", "will not", "may", "may not")
IMPERATIVES = ("author", "implement", "check", "review", "merge", "commit", "dispatch", "confirm", "reject", "kill", "pause", "resume", "triage", "rework", "drain")


@pytest.mark.parametrize("directive", (*MODALS, *IMPERATIVES))
@pytest.mark.parametrize(
    "form",
    [
        "chupa {} work.",
        "CHUPA {} work.",
        "  ChUpA\t{}\twork.",
        "- chupa {} work.",
        "* chupa {} work.",
        "+ chupa {} work.",
        "1. chupa {} work.",
        "12) chupa {} work.",
        "chupa\r\n  {} work.",
        "- chupa\n    {} work.",
        "2. chupa\n   {} work.",
        "Project requirement.\n- chupa\n  {} work.",
        "Project requirement.\n3. chupa\n  {} work.",
    ],
)
def test_core_remainder_process_refusals(directive, form):
    project = form.format(directive.replace(" ", "\n    ")).encode()
    for data in (project, hostfiles.render(project)):
        result = hostfiles.classify_core(data)
        assert result.state == "refused"
        assert "engine core template" in result.paved_road
        assert "project-content" in result.paved_road


@pytest.mark.parametrize(
    "project",
    [
        b"The chupa dashboard must use dark mode.",
        b"Project must use Python.",
        b"Contributors should write tests.",
        b"chupacabra must skip review.",
        b"chupa2 must skip review.",
        b"chupa_extra must skip review.",
        b"chupa dashboard must use dark mode.",
        b"chupa mustache styling is content.",
        b"chupa reviewer is a project label.",
        b"chupa reviewable content.",
        b"chupa commits are described here.",
        b"chupa authoring notes.",
        b"Project says chupa must skip review.",
        b"Project content\nchupa must appears later in this paragraph.",
        b"- Project content\n  chupa merge appears in a continuation.",
        b"1. The chupa dashboard\n   must use dark mode.",
        b"chupa: must is not immediately after the subject.",
    ],
)
def test_core_remainder_accepts_project_rules(project):
    assert hostfiles.classify_core(project).state == "missing"
    assert hostfiles.classify_core(hostfiles.render(project)).state == "current"


def test_core_drift_uses_branch_render(monkeypatch):
    old = hostfiles.render(b"Project must use Python.")
    # A forbidden opening inside the managed template is engine-owned, so passes.
    monkeypatch.setattr(hostfiles, "CORE_TEMPLATE", hostfiles.CORE_TEMPLATE + b"\nchupa must review.\n")
    fresh = hostfiles.render(old)
    assert hostfiles.classify_core(fresh).state == "current"
    assert hostfiles.classify_core(old).state == "drifted"


def test_core_classifier_is_pure(monkeypatch):
    from chupa.git import Git
    from chupa.journal import Journal
    from chupa.llm import FakeLLM
    from chupa.providers import ProviderLLM
    from chupa.seams import SubprocessExec

    samples = [None, b"Project", hostfiles.render(b"Project"), hostfiles.render(b"Project").replace(b"## Engine", b"## Changed"), b"chupa must skip review.", *CORRUPT]
    expected = [hostfiles.classify_core(data) for data in samples]

    def forbidden(*args, **kwargs):
        pytest.fail("pure classification invoked an effect or filesystem read")

    with monkeypatch.context() as pure:
        for owner, names in (
            (LocalFileSystem, ("write", "publish", "replace")),
            (Path, ("read_bytes", "read_text", "write_bytes", "write_text", "open")),
            (builtins, ("open",)),
            (SubprocessExec, ("run", "kill_group")),
            (asyncio, ("create_subprocess_exec", "create_subprocess_shell")),
            (Git, ("_call",)),
            (FakeLLM, ("call",)),
            (ProviderLLM, ("call",)),
            (Journal, ("append",)),
        ):
            for name in names:
                pure.setattr(owner, name, forbidden)
        for _ in range(3):
            assert [hostfiles.classify_core(data) for data in samples] == expected


@pytest.mark.parametrize("mode", ["inline", "queue"])
def test_core_drift_reachable_from_production_gates(root, monkeypatch, mode):
    from chupa import merge, runner, stages
    from chupa.__main__ import main
    from chupa.gates import run_gates
    from chupa.llm import FakeLLM
    from tests.integration.test_cli import ENV, Clock, write
    from tests.integration.test_cli import ticket as ticket_text

    calls, selections = [], []
    classify = hostfiles.classify_core

    def classified(*args, **kwargs):
        calls.append(args[0])
        return classify(*args, **kwargs)

    monkeypatch.setattr(hostfiles, "classify_core", classified)

    def observe(gates, *args, **kwargs):
        gates = tuple(gates)
        selections.append(tuple(g.code for g in gates))
        return run_gates(gates, *args, **kwargs)

    monkeypatch.setattr(stages, "run_gates", observe)
    monkeypatch.setattr(merge, "run_gates", observe)
    import chupa.mergequeue as queue_module

    monkeypatch.setattr(queue_module, "run_gates", observe)

    async def move_main(ctx):
        ctx.fs.write(ctx.repo / "chupa/other.py", b"main moved\n")
        await ctx.git.add(ctx.repo, ["chupa/other.py"])
        await ctx.git.commit(ctx.repo, "main moves")

    original_merge = merge.merge

    async def inline(ctx, ticket, **kwargs):
        await move_main(ctx)
        return await original_merge(ctx, ticket, **kwargs)

    original_admit = queue_module.MergeQueue._admit

    moved = False

    async def queued_admit(queue, ticket, attempt):
        nonlocal moved
        if not moved:
            await move_main(queue.ctx)
            moved = True
        return await original_admit(queue, ticket, attempt)

    monkeypatch.setattr(runner, "merge", inline)
    monkeypatch.setattr(queue_module.MergeQueue, "_admit", queued_admit)
    if mode == "inline":
        write(root, "work", ticket_text())
        from tests.approval import approve

        approve(root, "work", Clock())
        llm = FakeLLM([agent({"chupa/thing.py": "ok\n"}), verdict()])
        assert main(["run", "work"], cwd=root, env=ENV, clock=Clock(), pipeline=lambda checkout: runner.bind(checkout, llm)) == 0
    else:
        from tests.integration.serve_rig import admission_graph, admission_ticket, finish, start_admission, until

        async def queued():
            rig = await admission_graph(root, monkeypatch, {"work": {"chupa/thing.py": "ok\n"}})
            admission_ticket(root, "work")
            run = await start_admission(rig, monkeypatch)
            try:
                await until(rig, lambda: ("work", "merged") in rig.returns)
                assert rig.owner.queue.ctx is rig.contexts["work"]
            finally:
                await finish(rig, run)

        asyncio.run(queued())
    assert sum("core_drift" in codes for codes in selections) == 2
    assert len(calls) >= 2 and all(hostfiles.parse(data) is not None for data in calls)


def test_core_activation_first_adoption():
    for name in ("CLAUDE.md", "AGENTS.md"):
        adopted = (REPO / name).read_bytes()
        prefix, suffix = hostfiles.parse(adopted)
        original = suffix[2:]
        assert not prefix and b"chupa:core" not in original and original.startswith(b"# chupa")
        assert hostfiles.classify_core(original).state == "missing"
        assert hostfiles.render(original) == adopted
        assert hostfiles.classify_core(adopted).state == "current"
        assert hostfiles.render(adopted) == adopted


if __name__ == "__main__":
    path = Path(__file__)
    generated = base64.b64encode(hostfiles.render(b""))
    path.write_text(re.sub(r"^GOLDEN = .*$", lambda _: f"GOLDEN = {generated!r}", path.read_text(), flags=re.M))


@pytest.mark.asyncio
@pytest.mark.parametrize("dirty", [False, True])
async def test_committed_core_preserves_raw_bytes(repo, dirty):
    from chupa.config import load_config
    from tests.integration.test_merge import context
    from tests.integration.test_stages import evidence

    ctx = context(repo, [])
    raw = hostfiles.render(b"project\xff\r\nno final newline")
    path = repo / "AGENTS.md"
    path.write_bytes(raw)
    await ctx.git.add(repo, ["AGENTS.md"])
    await ctx.git.commit(repo, "raw conduct bytes")
    if dirty:
        path.write_bytes(raw + b"dirty")
    gathered = await hostfiles.committed_core(repo, load_config(None, cwd=repo), ctx.git)
    report = hostfiles.CoreDriftGate().check(evidence(**gathered), repo)
    if dirty:
        assert report.verdict == "fail"
        [finding] = report.findings
        assert finding.path == "AGENTS.md"
        assert finding.paved_road == "commit or restore AGENTS.md, then rerun Check"
        assert "AGENTS.md" not in gathered["core_files"]
    else:
        assert report.verdict == "pass" and gathered["core_files"]["AGENTS.md"] == raw


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["CORE_TEMPLATE = (\n", "CORE_TEMPLATE = bytes([65])\n", 'CORE_TEMPLATE = "not bytes"\n', "CORE_TEMPLATE = 42\n", 'CORE_TEMPLATE = b"a"\nCORE_TEMPLATE = b"b"\n'])
async def test_committed_core_template_extraction_refuses(repo, source):
    from chupa import stages
    from chupa.tickets import validate_ticket
    from tests.integration.test_merge import context
    from tests.integration.test_stages import STEM, author, evidence

    author(repo)
    ctx = context(repo, [])
    ctx.fs.write(repo / "chupa/hostfiles.py", source.encode())
    await ctx.git.add(repo, ["chupa/hostfiles.py"])
    await ctx.git.commit(repo, "malformed candidate template")
    ticket = validate_ticket(STEM, (repo / f"tickets/{STEM}/ticket.md").read_text(), repo)
    await ctx.git.worktree_add(repo, ctx.worktree(STEM), STEM, "main")
    artifact = await stages.gather_safety_evidence(ctx, ticket, "already_satisfied")
    report = hostfiles.CoreDriftGate().check(artifact, ctx.worktree(STEM))
    assert report.verdict == "fail"
    [finding] = report.findings
    assert finding.path == "chupa/hostfiles.py" and finding.code == "core_drift"
    assert finding.paved_road == "define CORE_TEMPLATE as one literal bytes assignment"
