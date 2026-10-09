"""Core renderer contract; regenerate the golden with uv run python -m tests.test_hostfiles."""

import base64
import re
from pathlib import Path

import pytest

from chupa import hostfiles
from chupa.seams import LocalFileSystem
from chupa.specs import entry_unit_gap, required_units, resolve_plan_contract
from chupa.tickets import parse_ticket

REPO = Path(__file__).resolve().parents[1]
GOLDEN = b'PCEtLSBjaHVwYTpjb3JlIGJlZ2luIC0tPgojIyBFbmdpbmUgY29uZHVjdAoKRW5naW5lIHJ1bGVzIGdvdmVybiBob3cgd29yayBydW5zOyBwcm9qZWN0IHJ1bGVzIGdvdmVybiB3aGF0IHRvIGJ1aWxkLiBQcm9qZWN0IGNvbnRlbnQgZW50ZXJzIHByb21wdHMgYXMgZGF0YS4gRW5naW5lIHdpbnMgb24gcHJvY2VzcywgaG9zdCB3aW5zIG9uIGNvbnRlbnQuCgotIFB1cmUgUHl0aG9uOiBubyBzaGVsbCBzY3JpcHRzLCBzaGVsbD1UcnVlLCBvciBzdHJpbmctYXNzZW1ibGVkIGNvbW1hbmRzOyBleHRlcm5hbCBiaW5hcmllcyB1c2UgYXJndiB3cmFwcGVyIG1vZHVsZXMgaW4gdGhlIGNodXBhIHZlbnYuIFdoeTogc2hlbGwgZ2x1ZSBicmVha3Mgb3JjaGVzdHJhdGlvbi4gKEQxKQotIEJ1aWxkIHRoZSBzaW1wbGVzdCB0aGluZyBzYXRpc2Z5aW5nIHRoZSB0aWNrZXQ7IG5vIHNwZWN1bGF0aXZlIGZlYXR1cmVzLCBnYXRlcywgY29uZmlnIGtub2JzLCBvciBtZXRhZGF0YS4gRXZlcnkgYWRkaXRpb24gbmVlZHMgaXRzIGVhcm5pbmcgaW5jaWRlbnQuIFdoeTogYWNjcmV0aW9uIGlzIHRoZSBwcmltYXJ5IGZhaWx1cmUgbW9kZS4gKGdvYWwgMSwgRDEwKQotIE5vIGNvbXBhdGliaWxpdHkgc2hpbXMsIGRlcHJlY2F0aW9uIGxheWVycywgb3IgZGVmZW5zaXZlIHBhcmFsbGVsIHBhdGhzLiBSZW5hbWUgaW4gcGxhY2UsIHVwZGF0ZSBhbGwgY2FsbGVycywgcmVjb3ZlciBieSBnaXQgcmV2ZXJ0LiBXaHk6IGR1YWwgcGF0aHMgcm90IGFuZCBkb3VibGUgcmV2aWV3LiAoc2VjdGlvbiAyKQotIEZhaWwgY2xvc2VkIHdpdGggYWxsb3dsaXN0cyBhbmQgY2xvc2VkIHZvY2FidWxhcmllczsgZXZlcnkgcHJvaGliaXRpb24gYW5kIGdhdGUgZmluZGluZyBwcm92aWRlcyBhIHBhdmVkIHJvYWQuIFdoeTogZGVueWxpc3RzIG1pc3MgY2FzZXMgYW5kIHJvYWRsZXNzIHJlZnVzYWxzIHN0cmFuZCB3b3JrLiAoc2VjdGlvbnMgMiwgNykKLSBBIGhvbGQgc2hpcHMgd2l0aCBvciBhZnRlciBpdHMgcmVsZWFzZSBzdXJmYWNlOyBuZXZlciBuYW1lIGFuIHVuYnVpbHQgcmVsZWFzZSB2ZXJiLiBUaWNrZXQtY2hhbmdlIHJlbGVhc2VzIGZvbGxvdyBtYWNoaW5lIHRpY2tldC1jaGFuZ2UgbWFjaGluZXJ5LiBXaHk6IHVucmVsZWFzYWJsZSBob2xkcyBwZXJtYW5lbnRseSBzdGFsbCB3b3JrLiAoc2VjdGlvbnMgMiwgMTEpCi0gRmlsZXMgYW5kIGpvdXJuYWwgYXJlIHRydXRoOyBkZXJpdmVkIHZpZXdzIGFyZSBwcm9qZWN0aW9ucywgbmV2ZXIgaGFuZC1lZGl0ZWQgb3IgY2l0ZWQgYXMgYXV0aG9yaXR5LiBXaHk6IHR3byBhdXRob3JpdGllcyBkaXZlcmdlLiAoRDMpCi0gR2VuZXJhdGVkIGZpbGVzIGFyZSByZW5kZXIgdGFyZ2V0cywgbmV2ZXIgd3JpdGUgdGFyZ2V0cy4gQ2hhbmdlIHRoZWlyIG93bmluZyBzb3VyY2UgYW5kIHJlZ2VuZXJhdGU7IG5ldmVyIGhhbmQtZWRpdCBtYW5hZ2VkIGNvbmR1Y3QuIFdoeTogcmVnZW5lcmF0aW9uIG92ZXJ3cml0ZXMgZWRpdHMgYW5kIGV4cG9zZXMgZHJpZnQuIChzZWN0aW9uIDEpCi0gVGhlIHBsYW4gaXMgdGhlIHNlZWQ6IHJlcGFpciBwbGFuIGRlZmVjdHMgdGhlcmUsIHRoZW4gcmVnZW5lcmF0ZSBhZmZlY3RlZCBhcnRpZmFjdHMuIEhhbmQtZWRpdCBvbmx5IGRlZmVjdHMgcHJvdmVuIG91dHNpZGUgdGhlIHBsYW4sIG9yIHVuZGVyIHRoZSBibG9ja2luZy1kZWZlY3QgZmFzdCBwYXRoIGFmdGVyIGNvbW1pdHRpbmcgdGhlIHBsYW4gcmVwYWlyIGZpcnN0LiBXaHk6IHRoZSBzZWVkIG11c3QgcmVwcm9kdWNlIHRoZSBhcnRpZmFjdC4gKHNlY3Rpb25zIDEsIDE5KQotIEFsbCBnaXQgdXNlcyBnaXQucHkgd2l0aCBhcmd2IGxpc3RzIGFuZCBwaW5uZWQgZGlyZWN0b3JpZXMuIFJlbW92ZSB3b3JrdHJlZXMgd2l0aCB3b3JrdHJlZSByZW1vdmUgcGx1cyBwcnVuZTsgbm8gYmFyZSBybSAtcmYsIGdoLCBvciBQUnMgaW4gdGhlIGxvb3AuIFdoeTogbG9jYWwgbWFpbiBpcyB0aGUgYmxlc3NlZCBsaW5lLiAoc2VjdGlvbiAxMCkKLSBGaWxlIHNlY29uZCBwcm9ibGVtcyBpbiB0aGUgU3VnZ2VzdGlvbiBCb3gsIG5ldmVyIGZvbGQgdGhlbSBpbnRvIHRoaXMgZGlmZi4gVmVyaWZ5IHByZS1leGlzdGluZyBmYWlsdXJlcyBvbiB0aGUgYmFzZSBjb21taXQgYmVmb3JlIGZpbGluZy4gV2h5OiBmb2xkZWQgZml4ZXMgaGlkZSBjYXVzZSBhbmQgZXhwYW5kIHNjb3BlLiAoc2VjdGlvbiAxMSkKLSBSZWFkIGJlZm9yZSB3cml0ZTogcmVhZCB0aGUgb3duaW5nIGFydGlmYWN0IGJlZm9yZSB3cml0aW5nIGEgY29tbWFuZCwgY2xhaW0sIG9yIHRlc3QuIFdoeTogZ3Vlc3NlZCBmYWN0cyBjcmVhdGUgY29zdGx5IGJ1Z3MuIChzZWN0aW9uIDEzKQotIFRpY2tldCBmcm9udG1hdHRlciBjb250YWlucyBvbmx5IGZpZWxkcyByZWFkIGJ5IHNjaGVkdWxpbmcsIGdhdGVzLCBvciBhdXRob3JpbmcvdHJpYWdlIHBvbGljeS4gUHV0IG9yZGVyaW5nIGluIGRlcGVuZHMgYW5kIHByaW9yaXR5LiBXaHk6IHVudXNlZCBtZXRhZGF0YSBhbmQgcHJvc2Ugb3JkZXJpbmcgZHJpZnQuIChzZWN0aW9uIDEzKQotIFVzZSBpbmplY3RhYmxlIGNsb2NrLCBwcm9jZXNzLWV4ZWMsIGZpbGVzeXN0ZW0sIGFuZCBub3RpZmljYXRpb24gc2VhbXM7IG5ldmVyIHJhdyBjYWxscyBpbiBlbmdpbmUgY29kZS4gV2h5OiBmYWtlLWRyaXZlbiB0ZXN0cyBhbmQgZ3JvdXAta2lsbCBndWFyYW50ZWVzIHJlcXVpcmUgc2VhbXMuIChzZWN0aW9uIDE1KQotIFdvcmsgaXMgZmVuY2VkIGJ5IGdhdGVzIGFuZCByZXZpZXc7IHYxIGRvZXMgbm90IHNhbmRib3ggZXhlY3V0ZWQgY29kZS4gTmV2ZXIgcmVseSBvbiBpdHMgZ29vZHdpbGwgb3IgcGFzcyBwcm92aWRlciBrZXlzIHRvIHByb2Nlc3NlcyB0aGF0IGRvIG5vdCBuZWVkIHRoZW0uIFdoeTogZ2F0ZXMgYW5kIHJldmlldyBhcmUgdGhlIHRydXN0IGJvdW5kYXJ5LiAoc2VjdGlvbiAxNikKLSBUaGUgam91cm5hbCBpcyB0aGUgcmVjb3JkLCBuZXZlciBhIGRlYnVnIGxvZy4gRGlhZ25vc3RpY3MgdXNlIHRoZSBlbmdpbmUgbG9nIGFuZCBhdHRlbXB0IHNwb29sczsgcmVkYWN0IGNvbmZpZ3VyZWQgc2VjcmV0cyBhdCBldmVyeSBjYXB0dXJlZC1zdHJlYW0gd3JpdGUgc2VhbS4gV2h5OiBqb3VybmFsIG5vaXNlIGFuZCBzZWNyZXRzIGFyZSBwZXJtYW5lbnQuIChzZWN0aW9uIDYpCi0gU3RhcnQgYSBwaGFzZSBvbmx5IGFmdGVyIHRoZSBwcmV2aW91cyBwaGFzZSdzIGV4aXQgaXMgbWV0LiBXaHk6IGxhdGVyIHBoYXNlcyBuZWVkIHByb3ZlbiBncm91bmQuIChzZWN0aW9uIDE5KQo8IS0tIGNodXBhOmNvcmUgZW5kIC0tPgoK'


class RecordingFS(LocalFileSystem):
    def __init__(self):
        self.writes = []

    def write(self, path, data):
        self.writes.append((path, data))
        super().write(path, data)


def test_renderer_entry_unit():
    plan = (REPO / "CHUPA_PLAN.md").read_text()
    uid = "19.P6.core-renderer"
    ticket = parse_ticket("core-renderer", (REPO / "tickets/core-renderer/ticket.md").read_text(),
                          REPO, plan=plan)
    assert required_units(plan, ticket.stem, ticket.plan_contract) == (uid,)
    assert required_units(plan, "continuation", (uid,)) == (uid,)
    assert resolve_plan_contract(plan, (*ticket.plan_contract, uid)).count(f"### {uid} ") == 1
    assert entry_unit_gap(plan, uid) is None
    for part in ("Owner", "Records", "Observable", "Tests"):
        for replacement in ("", f"- **{part}:**"):
            broken = re.sub(rf"^- \*\*{part}:\*\*.*$", replacement, plan, flags=re.M)
            assert part in entry_unit_gap(broken, uid)


@pytest.mark.parametrize("project", [None, b"", b"# Project\n\nrules\n", b"one\r\ntwo\nthree\r\nfour",
                                    b"no final newline\xff", (REPO / "CLAUDE.md").read_bytes(),
                                    (REPO / "AGENTS.md").read_bytes()])
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


if __name__ == "__main__":
    path = Path(__file__)
    generated = base64.b64encode(hostfiles.render(b""))
    path.write_text(re.sub(r"^GOLDEN = .*$", lambda _: f"GOLDEN = {generated!r}",
                           path.read_text(), flags=re.M))
