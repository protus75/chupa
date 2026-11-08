from chupa.graph import layout


def row(stem, section, *depends):
    return {"stem": stem, "section": section, "depends": list(depends)}


def test_branch_parents_share_existing_lane():
    graphs = layout([row("a", "queued", "d"), row("b", "queued", "d"), row("c", "queued"), row("d", "running")])
    # Opening a second branch for b would leave two d lanes alongside c.
    assert [lane["id"] for lane in graphs[1]["lanesOut"]] == ["d"]


def test_blocked_edges_only_target_blocked_rows():
    graphs = layout([row("a", "blocked", "b", "c"), row("b", "blocked"), row("c", "queued"), row("d", "running")])
    # Retaining the queued dependency would open an extra c lane above the queue.
    assert graphs[0]["parents"] == ["b"]
    assert layout([row("a", "blocked", "b"), row("b", "queued")])[0]["parents"] == []  # No implicit main-line edge.


def test_lanes_keep_opening_row_section():
    graphs = layout([row("a", "queued", "d"), row("b", "running"), row("c", "queued"), row("d", "running")])
    # The dependency lane retains the section of the row that opened it.
    assert graphs[1]["lanesOut"] == [{"id": "d", "section": "queued"}]
    assert graphs[1]["kind"] == "head"  # Running rows receive the head marker.


def test_first_parent_and_transitive_reduction_and_lane_order():
    graphs = layout([row("a", "queued", "d", "c", "b"), row("b", "queued", "c"), row("c", "queued"), row("d", "running"), row("e", "merged")])
    # b is the row below, c is reachable through b, and d remains a branch.
    assert graphs[0]["parents"] == ["b", "d"]
    # A merged row does not become a parent of a running row.
    assert graphs[3]["parents"] == []
    ordered = layout([row("a", "queued", "d", "c"), row("b", "queued"), row("c", "queued"), row("d", "running")])
    assert ordered[0]["parents"] == ["c", "d"]  # Dependencies follow position, not ticket order.


def test_held_gap_preserves_neighbor_until_next_row():
    graphs = layout([row("a", "queued", "d"), row("b", "queued", "d"), row("c", "queued"), row("d", "running"), row("e", "merged")])
    # The shared dependency uses one lane, which closes at d.
    assert graphs[3]["lanesIn"] == [{"id": "d", "section": "queued"}]
    assert graphs[3]["lanesOut"] == []


def test_edges_to_rows_above_are_dropped():
    graphs = layout([row("t", "blocked"), row("m", "blocked", "t"), row("run", "running"), row("x", "merged")])
    # A lane to t could never close, so it would run past the running and merged rows.
    assert graphs[1]["parents"] == []
    assert all(lane["id"] != "t" for graph in graphs[2:] for lane in graph["lanesIn"])


def test_new_tip_joins_existing_parent_lane():
    graphs = layout([row("m", "blocked", "t", "c"), row("s", "blocked", "t"), row("t", "blocked"), row("c", "blocked")])
    # A second t lane would hook back into t two rows later; s joins the lane m already opened.
    assert [lane["id"] for lane in graphs[1]["lanesOut"]] == ["c", "t"]
    assert graphs[1]["parentLanes"] == [1]
    assert graphs[0]["parentLanes"] == [0, 1]  # The first parent continues the node's own column.


def test_queued_parent_is_only_a_declared_dependency():
    assert layout([row("a", "queued"), row("b", "queued")])[0]["parents"] == []
    graph = layout([row("a", "queued", "b"), row("b", "queued")])[0]
    assert graph["parents"] == ["b"]
    assert graph["parentLanes"] == [len(graph["lanesIn"])]


def test_merged_history_does_not_join_running_rows():
    graphs = layout([row("a", "running"), row("b", "merged"), row("c", "merged")])
    assert graphs[0]["parents"] == []
    assert graphs[1]["parents"] == ["c"]
