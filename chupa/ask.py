"""Render engine-owned operator prompts."""

from pathlib import Path
from string import Template

from chupa import specs
from chupa.config import Config
from chupa.runner import SPECS_DIR
from chupa.tickets import ticket_path

KINDS = ("diagnose", "running", "review", "box", "drafts", "drain-loop")


def render(kind: str, stem: str, config: Config, repo: Path) -> str:
    if kind not in KINDS:
        raise ValueError(f"unknown prompt kind: {kind}")
    state = config.state_dir.resolve()
    root = repo.resolve()
    state_dir = state.relative_to(root) if state.is_relative_to(root) else state
    if kind == "box":
        from chupa.box import Box
        from chupa.seams import LocalFileSystem

        box = Box(state / "box", LocalFileSystem())
        messages = [box.get(id) for id in stem]
        paths = "\n".join(f"- {m.id}: {state_dir / 'box' / box.path(m).name}" for m in messages)
        template = Template((SPECS_DIR / "ask" / "box.md").read_text())
        result = template.substitute(messages=paths)
    elif kind == "drain-loop":
        template = Template((SPECS_DIR / "ask" / "drain-loop.md").read_text())
        result = template.substitute(state_dir=str(state_dir))
    elif kind == "drafts":
        paths = "\n".join(f"- {item}: {ticket_path(item)}" for item in stem)
        template = Template((SPECS_DIR / "ask" / "drafts.md").read_text())
        result = template.substitute(tickets=paths, state_dir=str(state_dir))
    else:
        template = Template((SPECS_DIR / "ask" / f"{kind}.md").read_text())
        result = template.substitute(stem=stem, ticket=str(ticket_path(stem)), state_dir=str(state_dir))
    if config.ask_notes is not None:
        result += f"\n{specs.data_open('host_notes')}\n{specs.quote_payload(config.ask_notes)}\n{specs.data_close('host_notes')}\n"
    return result
