"""
Iterative force-free layout adjustment (Requirement 5).

The algorithm is deliberately simple and predictable:

1. Collect absolute bounds + render_bounds for every movable shape.
2. For each overlapping pair at the same hierarchy level, push them apart along
   the shorter axis of their overlap (with a configurable padding gap).
3. Shapes that are bound together move as a rigid group.
4. Children never escape their parent container.
5. Iterate until there are no overlaps or ``max_iterations`` is reached.

The function operates on a ``Diagram`` instance directly (not on serialized
XML) so callers can run it before `save_diagram` without any round-trip.
"""

from __future__ import annotations

from typing import Optional

from .diagram import Diagram
from .render_geometry import shape_render_bounds


def _connected_components(bindings: dict[str, set[str]]) -> list[set[str]]:
    """Collapse the bound_nodes graph into connected components."""
    visited: set[str] = set()
    groups: list[set[str]] = []
    for start in bindings:
        if start in visited:
            continue
        stack = [start]
        component: set[str] = set()
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            component.add(node)
            for neighbour in bindings.get(node, ()):
                if neighbour not in visited:
                    stack.append(neighbour)
        groups.append(component)
    return groups


def _build_binding_groups(diagram: Diagram) -> dict[str, frozenset[str]]:
    """Return a mapping ``shape_id -> frozenset(group members)``.

    Shapes with no bindings map to a single-element set.  Uses each shape's
    ``bound_nodes`` list as an undirected adjacency list.
    """
    adjacency: dict[str, set[str]] = {sid: set() for sid in diagram.shapes}
    for sid, shape in diagram.shapes.items():
        for other in shape.bound_nodes:
            if other in diagram.shapes:
                adjacency[sid].add(other)
                adjacency[other].add(sid)
    components = _connected_components(adjacency)
    result: dict[str, frozenset[str]] = {}
    for comp in components:
        fs = frozenset(comp)
        for m in comp:
            result[m] = fs
    # Any shape not yet present (e.g. if adjacency was empty) → single group.
    for sid in diagram.shapes:
        result.setdefault(sid, frozenset({sid}))
    return result


def _shape_render_rect(
    diagram: Diagram, shape_id: str
) -> tuple[float, float, float, float]:
    """Compute the shape's absolute render bounds (honouring overflow=visible)."""
    x, y, w, h = diagram._shape_abs_rect(shape_id)
    if w <= 0 or h <= 0:
        return x, y, w, h
    shape = diagram.shapes[shape_id]
    return shape_render_bounds((x, y, w, h), shape.label or "", shape.style or "")


def _overlap_delta(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> tuple[float, float]:
    """Given two overlapping rectangles, return the (dx, dy) to fully separate
    them along the shortest axis.  Positive dy means ``b`` is pushed down; etc.
    """
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    # Overlap sizes on each axis.
    ox = min(ax + aw, bx + bw) - max(ax, bx)
    oy = min(ay + ah, by + bh) - max(ay, by)
    if ox <= 0 or oy <= 0:
        return 0.0, 0.0
    if ox < oy:
        # Push along X.
        dx = ox if (bx + bw / 2.0) >= (ax + aw / 2.0) else -ox
        return dx, 0.0
    # Push along Y.
    dy = oy if (by + bh / 2.0) >= (ay + ah / 2.0) else -oy
    return 0.0, dy


def _apply_group_translation(
    diagram: Diagram,
    group: frozenset[str],
    dx: float,
    dy: float,
) -> None:
    """Shift every shape in ``group`` by (dx, dy) in their own local frame.

    Because drawio stores child coordinates relative to the parent, translating
    the shape's own ``x`` / ``y`` by the same delta works uniformly for both
    top-level shapes and children of containers (as long as we never move a
    group across parent boundaries — which we explicitly avoid).
    """
    for sid in group:
        if sid in diagram.shapes:
            diagram.shapes[sid].x += dx
            diagram.shapes[sid].y += dy


def _clamp_group_to_parents(
    diagram: Diagram,
    group: frozenset[str],
    margin: float,
) -> None:
    """Ensure every shape in the group stays inside its parent container.

    Shapes without a parent are unconstrained. For children of a container we
    clamp each shape's absolute bounds into the container's interior (minus
    ``margin``) and translate the whole group by the minimum correction.
    """
    corrections: list[tuple[float, float]] = []
    for sid in group:
        shape = diagram.shapes.get(sid)
        if shape is None or not shape.parent_id:
            continue
        parent = diagram.shapes.get(shape.parent_id)
        if parent is None:
            continue
        px, py, pw, ph = diagram._shape_abs_rect(shape.parent_id)
        sx, sy, sw, sh = diagram._shape_abs_rect(sid)
        if sw <= 0 or sh <= 0 or pw <= 0 or ph <= 0:
            continue
        dx = 0.0
        dy = 0.0
        if sx < px + margin:
            dx = (px + margin) - sx
        elif sx + sw > px + pw - margin:
            dx = (px + pw - margin) - (sx + sw)
        if sy < py + margin:
            dy = (py + margin) - sy
        elif sy + sh > py + ph - margin:
            dy = (py + ph - margin) - (sy + sh)
        if dx or dy:
            corrections.append((dx, dy))
    # Apply the largest correction in each axis so every member ends up inside.
    if corrections:
        max_dx = max((c[0] for c in corrections), key=abs)
        max_dy = max((c[1] for c in corrections), key=abs)
        if max_dx or max_dy:
            _apply_group_translation(diagram, group, max_dx, max_dy)


def adjust_layout(
    diagram: Diagram,
    padding: float = 10.0,
    max_iterations: int = 20,
    only_ids: Optional[list[str]] = None,
    dry_run: bool = False,
) -> dict:
    """Iteratively push overlapping shapes apart.

    Args:
        diagram: The target diagram (mutated unless ``dry_run``).
        padding: Extra gap to add between shapes after separation (px).
        max_iterations: Stop after this many passes if still unresolved.
        only_ids: If given, restrict movement to these shape IDs (their
            binding groups are still moved as a unit; un-listed bound
            members still follow).
        dry_run: When True, compute the moves but don't apply them.

    Returns:
        ``{"moves": [...], "iterations": N, "remaining_overlaps": [...]}``.
    """
    if dry_run:
        # Work on a deep copy so the caller's diagram is untouched.
        import copy
        work = copy.deepcopy(diagram)
    else:
        work = diagram

    # Record starting positions to compute per-shape delta reports.
    start_pos: dict[str, tuple[float, float]] = {
        sid: (float(s.x), float(s.y)) for sid, s in work.shapes.items()
    }

    groups_by_id = _build_binding_groups(work)
    only_set: Optional[set[str]] = set(only_ids) if only_ids else None

    def group_is_movable(group: frozenset[str]) -> bool:
        if only_set is None:
            return True
        return any(sid in only_set for sid in group)

    iterations_run = 0
    for _ in range(max(1, max_iterations)):
        iterations_run += 1
        any_moved = False

        shape_ids = list(work.shapes.keys())
        # Process same-parent pairs only: different hierarchy levels aren't
        # comparable (a child lives inside its container; the container
        # itself owns the child's footprint).
        for i, sid_a in enumerate(shape_ids):
            shape_a = work.shapes[sid_a]
            for sid_b in shape_ids[i + 1:]:
                shape_b = work.shapes[sid_b]
                if shape_a.parent_id != shape_b.parent_id:
                    continue
                # Skip UML-class section children (they share a shape parent
                # and are managed by UML rendering, not layout).
                if shape_a.parent_id and shape_a.parent_id in work.shapes:
                    if (shape_a.parent_id != shape_b.parent_id
                            or shape_a.width <= 0 or shape_b.width <= 0):
                        continue
                group_a = groups_by_id[sid_a]
                group_b = groups_by_id[sid_b]
                if group_a is group_b:
                    continue  # Same binding group — never push apart.

                a_rect = _shape_render_rect(work, sid_a)
                b_rect = _shape_render_rect(work, sid_b)
                dx, dy = _overlap_delta(a_rect, b_rect)
                if dx == 0.0 and dy == 0.0:
                    continue

                # Expand by padding, split the move between the two groups
                # according to which ones are movable.
                if dx != 0.0:
                    dx += padding if dx > 0 else -padding
                if dy != 0.0:
                    dy += padding if dy > 0 else -padding

                a_mov = group_is_movable(group_a)
                b_mov = group_is_movable(group_b)
                if not a_mov and not b_mov:
                    continue
                if a_mov and b_mov:
                    # Split equally — push b by half and a by the other half.
                    _apply_group_translation(work, group_b, dx / 2.0, dy / 2.0)
                    _apply_group_translation(work, group_a, -dx / 2.0, -dy / 2.0)
                elif b_mov:
                    _apply_group_translation(work, group_b, dx, dy)
                else:
                    _apply_group_translation(work, group_a, -dx, -dy)
                any_moved = True

        # After a pass of separation, clamp groups back into their containers.
        for group in {groups_by_id[sid] for sid in work.shapes}:
            if group_is_movable(group):
                _clamp_group_to_parents(work, group, margin=5.0)

        if not any_moved:
            break

    # After layout is settled, re-compute auto_route waypoints for any edges
    # whose endpoints moved. This keeps orthogonal edges cleanly routed.
    moves: list[dict] = []
    for sid, shape in work.shapes.items():
        ox, oy = start_pos.get(sid, (shape.x, shape.y))
        if (float(shape.x), float(shape.y)) != (ox, oy):
            moves.append({
                "shape_id": sid,
                "old": [ox, oy],
                "new": [float(shape.x), float(shape.y)],
            })

    if not dry_run and moves:
        # Re-route connections whose endpoints moved — only when the user
        # originally requested auto_route (we track this by assuming any edge
        # with no explicit waypoints is fair game for re-routing).
        moved_ids = {m["shape_id"] for m in moves}
        for conn in work.connections.values():
            if conn.source_id not in moved_ids and conn.target_id not in moved_ids:
                continue
            if conn.source_id not in work.shapes or conn.target_id not in work.shapes:
                continue
            # Only re-route when we produced the existing waypoints via
            # auto_route, heuristically: either no waypoints, or all existing
            # waypoints were along-axis (we can't recover intent for custom
            # routes). For safety we only re-route when waypoints is empty.
            if not conn.waypoints:
                conn.waypoints = work._compute_auto_waypoints(conn.source_id, conn.target_id)

    # Compute remaining overlaps for the report.
    remaining: list[tuple[str, str]] = []
    shape_ids = list(work.shapes.keys())
    for i, sid_a in enumerate(shape_ids):
        shape_a = work.shapes[sid_a]
        for sid_b in shape_ids[i + 1:]:
            shape_b = work.shapes[sid_b]
            if shape_a.parent_id != shape_b.parent_id:
                continue
            dx, dy = _overlap_delta(
                _shape_render_rect(work, sid_a),
                _shape_render_rect(work, sid_b),
            )
            if dx or dy:
                remaining.append((sid_a, sid_b))

    return {
        "moves": moves,
        "iterations": iterations_run,
        "remaining_overlaps": [{"shape1_id": a, "shape2_id": b} for a, b in remaining],
        "dry_run": dry_run,
    }
