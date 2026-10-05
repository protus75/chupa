"""Effect primitive (CHUPA_PLAN.md section 6): once-per-key against the surviving journal.

Once is COMPLETION-keyed: a key with a journaled completion replays its recorded
result. An intent with no completion (crash mid-effect) re-executes here on
purpose -- that window belongs to reconcile-on-entry (section 11), not this
primitive. `@effect(key=...)` sugar ships with its first call site.
"""

import json
from collections.abc import Awaitable, Callable
from typing import Any

from chupa.journal import EventType, Journal


class Effects:
    def __init__(self, journal: Journal) -> None:
        self._journal = journal
        # Startup scan; appended to as effects complete (D3: no index builder).
        self._completed = {
            e.key for e in journal.read() if e.type == EventType.EFFECT_COMPLETION and e.key is not None
        }

    async def run(self, action: Callable[[], Awaitable[Any]], *, key: str, ticket: str | None) -> Any:
        if not isinstance(key, str) or not key:
            raise ValueError(f"effect key must be a non-empty string, got {key!r}; join components with '/'")
        if key in self._completed:
            return self._recorded(key)

        self._journal.append(EventType.EFFECT_INTENT, {}, ticket=ticket, key=key)
        result = await action()
        try:
            encoded = json.dumps(result)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"effect {key!r} returned a non-JSON result ({exc}); return plain dicts/lists/str/numbers"
            ) from exc
        # Return the decoded record, not `result`, so executing and replaying yield identical values.
        recorded = json.loads(encoded)
        self._journal.append(EventType.EFFECT_COMPLETION, {"result": recorded}, ticket=ticket, key=key)
        self._completed.add(key)
        return recorded

    def _recorded(self, key: str) -> Any:
        for e in self._journal.read():
            if e.type == EventType.EFFECT_COMPLETION and e.key == key:
                return e.body["result"]
        raise AssertionError(f"completed key {key!r} has no completion event in the journal")
