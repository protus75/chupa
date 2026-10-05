"""Starting-state policy for box-authored tickets (plan section 12)."""

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, get_args

from chupa.box import MESSAGE_CLASSES
from chupa.config import BoxRow, Config, StartState
from chupa.llm import AgentTier
from chupa.providers import resolve
from chupa.specs import load_spec

BASELINE_SIGNAL = "review_baseline"
BASELINED_SURFACES = ("review", "author")
TIERS: tuple[AgentTier, ...] = get_args(AgentTier)
SPECS = Path(__file__).resolve().parent.parent / "specs"


def baseline_identity(config: Config, specs_dir: Path = SPECS) -> dict:
    """Return the current review and author routing rows and spec-major versions."""
    out = {}
    for surface in BASELINED_SURFACES:
        rows = {}
        for tier in TIERS:
            served = resolve(config, tier, surface)
            rows[tier] = {"provider": served.provider.name, "model": served.model}
        path = specs_dir / f"{surface}.md"
        major = int(load_spec(path.read_text()).meta.version.split(".")[0]) if path.exists() else None
        out[surface] = {"spec_major": major, "rows": rows}
    return out


def go_binds(events: Iterable[Any], identity: Mapping[str, Any]) -> bool:
    """Whether the latest review-baseline signal is a GO for this identity."""
    latest = None
    for event in events:
        body = event.body
        if event.type == "signal" and body.get("signal") == BASELINE_SIGNAL:
            latest = body
    return latest is not None and latest.get("verdict") == "GO" and latest.get("identity") == identity


def policy_row(message_class: str, bug_origin: str | None, has_repro: bool | None) -> BoxRow:
    """Map a box message's class-specific fields to its policy-table row."""
    if message_class == "bug_report":
        if bug_origin == "self_diagnosed" and has_repro is not None:
            return "bug_report_self_diagnosed"
        if bug_origin == "player" and has_repro is True:
            return "bug_report_player_repro"
        if bug_origin == "player" and has_repro is False:
            return "bug_report_player_no_repro"
        raise ValueError("bug_report requires bug_origin and has_repro")
    if message_class in MESSAGE_CLASSES:
        return message_class
    raise ValueError(f"unknown message class {message_class!r}")


def _path_overlap(left: str, right: str) -> bool:
    left, right = left.rstrip("/"), right.rstrip("/")
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def touches_inventory(fence: Sequence[str], inventory: Sequence[str]) -> bool:
    """Whether any scope-fence and safety-inventory paths overlap at a boundary."""
    return any(_path_overlap(fenced, protected) for fenced in fence for protected in inventory)


def start_state(
    config: Config,
    *,
    row: BoxRow,
    fence: Sequence[str],
    gate_bypass: Sequence[str],
    go: bool,
    reopen: bool = False,
) -> StartState:
    """Resolve a box ticket's initial state, failing closed for every override."""
    if (reopen or not go or not config.engine_plane_safety_inventory
            or touches_inventory(fence, config.engine_plane_safety_inventory) or gate_bypass):
        return "draft"
    return config.box_policy[row]
