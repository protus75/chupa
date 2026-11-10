import pytest

from chupa.tickets import context_conflicts, context_excerpt, render_context


def test_python_definitions_and_decorated_method():
    text = "x = 4\n\ndef other():\n    pass\n\nclass B:\n    @marked\n    async def run(self):\n        return 9\n\n    def skip(self):\n        pass\n"
    assert context_excerpt("m.py::x", text) == "x = 4\n"  # not another assignment or the whole file
    assert context_excerpt("m.py::B.run", text) == "    @marked\n    async def run(self):\n        return 9\n"  # includes decorator, excludes sibling


def test_heading_with_fenced_heading_and_subheading():
    text = "# One\n## Two\n```python\n# Two\n```\n### Two-a\nbody\n## Three\nend\n"
    assert context_excerpt("d.md#Two", text) == "## Two\n```python\n# Two\n```\n### Two-a\nbody\n"  # fenced heading is neither duplicate nor boundary


@pytest.mark.parametrize(
    ("entry", "text"),
    [
        ("m.py::Missing", "def present():\n    pass\n"),
        ("m.py#Two", None),
        ("d.md::B", None),
        ("d.md#Nope", "## Two\ncontent\n"),
        ("d.md#Two", "## Two\na\n## Two\nb\n"),
        ("image.png#x", None),
    ],
)
def test_invalid_sections_raise(entry, text):
    with pytest.raises(ValueError):  # neither an empty excerpt nor the whole file is accepted
        context_excerpt(entry, text)


def test_whole_and_sections_conflict():
    assert context_conflicts(["m.py", "m.py::B.run"]) == ["m.py"]  # mixed whole and section must be refused
    assert context_conflicts(["m.py::B.run", "m.py::B.stop"]) == []  # distinct sections are allowed


def test_render_context_reads_selected_heading():
    class Repo:
        def __truediv__(self, path):
            assert path == "d.md"  # selector is not part of the file path
            return self

        def read_text(self):
            return "# One\nother\n## Two\nselected\n## Three\nlast\n"

    assert render_context(Repo(), "d.md#Two") == "## Two\nselected\n"  # not the whole file


def test_render_context_propagates_decode_error():
    class Repo:
        def __truediv__(self, path):
            assert path == "image.png"  # the requested file is read
            return self

        def read_text(self):
            raise UnicodeDecodeError("utf-8", b"\x89", 0, 1, "invalid start byte")

    with pytest.raises(UnicodeDecodeError):  # decoding errors must reach lint
        render_context(Repo(), "image.png")
