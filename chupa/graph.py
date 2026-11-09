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
        if section == "merged":
            parents = [below] if below and sections[below] == "merged" else []
        else:
            parents = reduced

        incoming = [lane.copy() for lane in outgoing]
        outgoing = []
        parent_lanes = []
        for lane in incoming:
            if lane["id"] is None:
                continue
            if lane["id"] == stem:
                if not parent_lanes and parents:
                    parent_lanes.append(len(outgoing))
                    outgoing.append({"id": parents[0], "section": section})
                else:
                    outgoing.append({"id": None, "section": None})
            else:
                outgoing.append(lane.copy())
        while outgoing and outgoing[-1]["id"] is None:
            outgoing.pop()
        for parent in parents[len(parent_lanes) :]:
            # A parent that already has a lane is joined there, as `git log --graph` draws `|/`, instead of a second lane.
            existing = [index for index, lane in enumerate(outgoing) if lane["id"] == parent]
            if existing:
                parent_lanes.append(existing[-1])
            else:
                parent_lanes.append(len(outgoing))
                outgoing.append({"id": parent, "section": section})
        kind = "head" if section == "running" else "node"
        circle = next((index for index, lane in enumerate(incoming) if lane["id"] == stem), len(incoming))
        segments = []
        slot = 0
        for index, lane in enumerate(incoming):
            if lane["id"] is None:
                continue
            if lane["id"] == stem:
                if index != circle:
                    segments.append({"kind": "into", "from": index, "to": circle, "section": lane["section"]})
                slot += 1
            elif slot < len(outgoing) and lane["id"] == outgoing[slot]["id"]:
                if index == slot:
                    segments.append({"kind": "straight", "lane": index, "section": lane["section"]})
                else:
                    segments.append({"kind": "shift", "from": index, "to": slot, "section": lane["section"]})
                slot += 1
        for parent in parent_lanes:
            if parent == circle:
                node_section = outgoing[circle]["section"] if circle < len(outgoing) else incoming[circle]["section"] if circle < len(incoming) else section
                segments.append({"kind": "down", "lane": circle, "section": node_section})
            else:
                segments.append({"kind": "branch" if parent > circle else "join", "from": circle, "to": parent, "section": outgoing[parent]["section"]})
        if circle < len(incoming):
            segments.append({"kind": "top", "lane": circle, "section": incoming[circle]["section"]})
        result.append(
            {
                "kind": kind,
                "parents": parents,
                "parentLanes": parent_lanes,
                "lanesIn": incoming,
                "lanesOut": outgoing,
                "circle": circle,
                "dot": "head" if kind == "head" else "merge" if len(parents) > 1 else "node",
                "width": max(len(incoming), len(outgoing), circle + 1) + 1,
                "segments": segments,
            }
        )
    return result
