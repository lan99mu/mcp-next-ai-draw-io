"""Tests for adjust_layout / auto_layout_adjust (Requirement 5)."""

from mcp_drawio_server.auto_layout import adjust_layout
from mcp_drawio_server.diagram import Diagram


def _has_overlap_same_parent(diagram: Diagram) -> bool:
    shape_ids = list(diagram.shapes.keys())
    for i, sid_a in enumerate(shape_ids):
        a = diagram.shapes[sid_a]
        for sid_b in shape_ids[i + 1:]:
            b = diagram.shapes[sid_b]
            if a.parent_id != b.parent_id:
                continue
            ax, ay, aw, ah = diagram._shape_abs_rect(sid_a)
            bx, by, bw, bh = diagram._shape_abs_rect(sid_b)
            if aw <= 0 or bw <= 0:
                continue
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                return True
    return False


def test_adjust_layout_resolves_simple_overlap():
    d = Diagram()
    d.add_shape("A", x=0, y=0, width=120, height=60)
    # Heavy overlap with A.
    d.add_shape("B", x=30, y=10, width=120, height=60)
    assert _has_overlap_same_parent(d)
    result = adjust_layout(d, padding=10, max_iterations=20)
    assert result["moves"], "Expected at least one shape to move"
    assert not _has_overlap_same_parent(d)
    assert result["remaining_overlaps"] == []


def test_adjust_layout_respects_binding_group():
    d = Diagram()
    a = d.add_shape("A", x=0, y=0, width=120, height=60)
    b = d.add_shape("B", x=140, y=0, width=120, height=60)
    # A & B are bound, so the gap between them must remain constant.
    d.bind_shapes([a, b])
    c = d.add_shape("C", x=60, y=10, width=120, height=60)  # overlaps A

    orig_delta_x = d.shapes[b].x - d.shapes[a].x
    orig_delta_y = d.shapes[b].y - d.shapes[a].y

    adjust_layout(d, padding=10, max_iterations=20)

    # The bound pair must still have the same relative offset.
    new_delta_x = d.shapes[b].x - d.shapes[a].x
    new_delta_y = d.shapes[b].y - d.shapes[a].y
    assert (new_delta_x, new_delta_y) == (orig_delta_x, orig_delta_y)


def test_adjust_layout_dry_run_does_not_mutate():
    d = Diagram()
    d.add_shape("A", x=0, y=0, width=100, height=60)
    d.add_shape("B", x=20, y=0, width=100, height=60)

    snapshot = {sid: (s.x, s.y) for sid, s in d.shapes.items()}
    result = adjust_layout(d, dry_run=True)
    assert result["moves"], "Dry run should still compute would-be moves"
    assert result["dry_run"] is True
    for sid, (ox, oy) in snapshot.items():
        assert (d.shapes[sid].x, d.shapes[sid].y) == (ox, oy)


def test_adjust_layout_keeps_children_inside_container():
    d = Diagram()
    container = d.add_shape(
        "C", x=0, y=0, width=400, height=200, shape_type="container"
    )
    # Two siblings inside C that overlap each other.
    d.add_shape("c1", x=10, y=20, width=100, height=60, parent_id=container)
    d.add_shape("c2", x=40, y=30, width=100, height=60, parent_id=container)
    adjust_layout(d, padding=5, max_iterations=30)

    # Both children must still sit strictly inside the container's bounds.
    cx, cy, cw, ch = d._shape_abs_rect(container)
    for sid in ("c1", "c2"):
        # look up by label (we don't know generated IDs here since we passed custom ones)
        shape = next(s for s in d.shapes.values() if s.label == sid)
        sx, sy, sw, sh = d._shape_abs_rect(shape.id)
        assert sx >= cx - 1
        assert sy >= cy - 1
        assert sx + sw <= cx + cw + 1
        assert sy + sh <= cy + ch + 1


def test_adjust_layout_only_ids_restricts_movement():
    d = Diagram()
    a = d.add_shape("A", x=0, y=0, width=100, height=60)
    b = d.add_shape("B", x=30, y=10, width=100, height=60)  # overlaps A

    orig_a = (d.shapes[a].x, d.shapes[a].y)
    adjust_layout(d, only_ids=[b], padding=10)
    # A must not have been moved because it's not in only_ids and not bound to b.
    assert (d.shapes[a].x, d.shapes[a].y) == orig_a
    # B must have moved.
    assert (d.shapes[b].x, d.shapes[b].y) != (30, 10)
