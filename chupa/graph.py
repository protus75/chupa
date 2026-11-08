"""Pure layout for the ticket graph, ordered from top to bottom."""


def layout(rows: list[dict]) -> list[dict]:
    position = {row["stem"]: i for i, row in enumerate(rows)}
    sections = {row["stem"]: row["section"] for row in rows}
    # A lane closes only at a later row: an edge to a row above would run past every row below, so it is dropped.
    deps = {row["stem"]: [d for d in row["depends"] if d in sections and sections[d] != "merged" and position[d] > position[row["stem"]]] for row in rows}

    def descendants(stem):
        seen = set()
        pending = list(deps[stem])
        while pending:
            dependency = pending.pop()
            if dependency not in seen:
                seen.add(dependency)
                pending.extend(deps[dependency])
        return seen

    def lane_key(stem):
        return (1, -position[stem]) if sections[stem] == "blocked" else (0, position[stem])

    result = []
    outgoing = []
    for i, row in enumerate(rows):
        stem, section = row["stem"], row["section"]
        dependencies = deps[stem]
        if section == "blocked":
            dependencies = [d for d in dependencies if sections[d] == "blocked"]
        reduced = sorted((d for d in dependencies if not any(d != other and d in descendants(other) for other in dependencies)), key=lane_key)
        below = rows[i + 1]["stem"] if i + 1 < len(rows) else None
        if section == "blocked":
            parents = reduced
        else:
            branches = [] if section == "merged" else [d for d in reduced if d != below]
            parents = ([below] if below else []) + branches

        incoming = [lane.copy() for lane in outgoing]
        outgoing = []
        first_added = False
        for lane in incoming:
            if lane["id"] is None:
                continue
            if lane["id"] == stem:
                if not first_added and parents:
                    outgoing.append({"id": parents[0], "section": section})
                    first_added = True
                else:
                    outgoing.append({"id": None, "section": None})
            else:
                outgoing.append(lane.copy())
        while outgoing and outgoing[-1]["id"] is None:
            outgoing.pop()
        for index in range(1 if first_added else 0, len(parents)):
            parent = parents[index]
            if index and any(lane["id"] == parent for lane in outgoing):
                continue
            outgoing.append({"id": parent, "section": section})
        result.append({"kind": "head" if section == "running" else "node", "parents": parents, "lanesIn": incoming, "lanesOut": outgoing})
    return result
