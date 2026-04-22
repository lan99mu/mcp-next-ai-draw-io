"""
Utility module for detecting shape overlaps in Draw.io diagrams.

Two kinds of problems are detected:
1. **Node–node overlaps**: two sibling vertex shapes whose absolute bounding
   boxes intersect (after resolving nested parent offsets).
2. **Out-of-container violations**: a vertex shape whose parent_id refers to an
   actual container shape, but the child's absolute bounding box extends outside
   the container's absolute bounding box.

Both results include actionable suggestions so the AI model can fix the layout.
"""

from __future__ import annotations

import re
from typing import Optional

from .render_geometry import (
    edge_label_rect,
    parse_style,
    segment_intersects_rect,
    shape_render_bounds,
)


_DEFAULT_ROOT_IDS = {"0", "1"}


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _safe_float(value, default: float = 0.0) -> float:
    """Convert *value* to float, returning *default* on failure."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _absolute_bounds(
    cell: dict,
    cells_by_id: dict[str, dict],
    _seen: Optional[set[str]] = None,
) -> tuple[float, float, float, float]:
    """Return the absolute (x, y, width, height) of *cell*.

    Recursively resolves the parent chain to convert relative coordinates into
    canvas-absolute coordinates.  A ``_seen`` set prevents infinite loops if
    the XML somehow contains a circular parent reference.
    """
    x = _safe_float(cell.get("x"))
    y = _safe_float(cell.get("y"))
    width = _safe_float(cell.get("width"))
    height = _safe_float(cell.get("height"))

    parent_id = cell.get("parent")
    if parent_id and parent_id not in _DEFAULT_ROOT_IDS:
        cell_id = cell.get("id")
        if _seen is None:
            _seen = set()
        if cell_id and cell_id not in _seen:
            _seen.add(cell_id)
            parent = cells_by_id.get(parent_id)
            if parent and parent.get("vertex"):
                px, py, _, _ = _absolute_bounds(parent, cells_by_id, _seen)
                x += px
                y += py

    return x, y, width, height


def _boxes_overlap(
    ax: float, ay: float, aw: float, ah: float,
    bx: float, by: float, bw: float, bh: float,
) -> bool:
    """Return True when two axis-aligned bounding boxes intersect."""
    return (
        ax < bx + bw and bx < ax + aw
        and ay < by + bh and by < ay + ah
    )


def _box_contains(
    cx: float, cy: float, cw: float, ch: float,
    ix: float, iy: float, iw: float, ih: float,
) -> bool:
    """Return True when the container (c*) fully contains the inner box (i*)."""
    return (
        cx <= ix and cy <= iy
        and cx + cw >= ix + iw
        and cy + ch >= iy + ih
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_overlaps(cells: list[dict]) -> dict:
    """Detect shape overlaps and out-of-container boundary violations.

    Args:
        cells: All cells (shapes **and** connections) from the diagram.

    Returns:
        A dictionary with three keys:

        ``node_overlaps``
            List of dicts, one per overlapping pair of sibling shapes::

                {
                    "shape1_id": str,
                    "shape1_label": str,
                    "shape1_bounds": [x, y, x2, y2],   # absolute canvas coords
                    "shape2_id": str,
                    "shape2_label": str,
                    "shape2_bounds": [x, y, x2, y2],
                    "overlap_area": [ox, oy, ox2, oy2],  # intersection rectangle
                    "suggestion": str,
                }

        ``out_of_container``
            List of dicts, one per shape that escapes its container::

                {
                    "shape_id": str,
                    "shape_label": str,
                    "shape_bounds": [x, y, x2, y2],
                    "container_id": str,
                    "container_label": str,
                    "container_bounds": [x, y, x2, y2],
                    "suggestion": str,
                }

        ``label_overlaps``
            List of dicts describing edge labels that visually overlap either
            an unrelated node's body or another edge's label.  Entries carry
            ``issue_type`` = ``edge_label_over_node`` or
            ``edge_label_over_edge_label`` plus the participating IDs,
            rendered bounds, and a repair suggestion.
    """
    vertices = [c for c in cells if c.get("vertex")]
    cells_by_id: dict[str, dict] = {c["id"]: c for c in cells}

    # Pre-compute absolute bounds for all vertices
    abs_bounds: dict[str, tuple[float, float, float, float]] = {}
    render_bounds: dict[str, tuple[float, float, float, float]] = {}
    for v in vertices:
        cb = _absolute_bounds(v, cells_by_id)
        abs_bounds[v["id"]] = cb
        # render_bounds = cell bounds, expanded when overflow=visible label escapes
        render_bounds[v["id"]] = shape_render_bounds(
            cb, v.get("value") or "", v.get("style") or ""
        )

    # Identify container shapes: shapes that have at least one child vertex
    parent_ids_in_use: set[str] = set()
    for v in vertices:
        pid = v.get("parent")
        if pid and pid not in _DEFAULT_ROOT_IDS:
            parent_ids_in_use.add(pid)
    container_ids = parent_ids_in_use & set(abs_bounds.keys())

    # -----------------------------------------------------------------------
    # 1.  Node–node overlap (only among shapes sharing the same parent level)
    # -----------------------------------------------------------------------
    node_overlaps: list[dict] = []
    for i, shape1 in enumerate(vertices):
        for shape2 in vertices[i + 1:]:
            # Skip if one is a known UML section child (parent is a shape that
            # is itself not a container of peer nodes — heuristic: both must
            # share the same parent to be considered "siblings").
            p1 = shape1.get("parent", "1")
            p2 = shape2.get("parent", "1")
            if p1 != p2:
                continue  # different levels — not direct siblings

            # Skip UML section cells: they have a shape as parent AND are very
            # narrow / zero-x, which produces spurious overlaps.
            # We detect them by the parent being a non-root shape AND having
            # zero-width or text/line style.
            style1 = (shape1.get("style") or "").lower()
            style2 = (shape2.get("style") or "").lower()
            if _is_uml_section(style1) or _is_uml_section(style2):
                continue

            ax, ay, aw, ah = abs_bounds[shape1["id"]]
            bx, by, bw, bh = abs_bounds[shape2["id"]]

            if aw <= 0 or ah <= 0 or bw <= 0 or bh <= 0:
                continue

            # First check the cell bounds (the body overlap case).
            body_overlap = _boxes_overlap(ax, ay, aw, ah, bx, by, bw, bh)

            # Then also check the render bounds — this catches the case
            # where overflow=visible labels escape their cell and visually
            # overlap a neighbouring shape.
            rax, ray, raw, rah = render_bounds[shape1["id"]]
            rbx, rby, rbw, rbh = render_bounds[shape2["id"]]
            render_overlap = _boxes_overlap(rax, ray, raw, rah, rbx, rby, rbw, rbh)

            if not body_overlap and not render_overlap:
                continue

            cause = "body" if body_overlap else "label_overflow"
            ux, uy, uw, uh = (
                (ax, ay, aw, ah) if body_overlap else (rax, ray, raw, rah)
            )
            vx, vy, vw, vh = (
                (bx, by, bw, bh) if body_overlap else (rbx, rby, rbw, rbh)
            )
            ox1 = max(ux, vx)
            oy1 = max(uy, vy)
            ox2 = min(ux + uw, vx + vw)
            oy2 = min(uy + uh, vy + vh)

            entry = {
                "shape1_id": shape1["id"],
                "shape1_label": _label(shape1),
                "shape1_bounds": [ax, ay, ax + aw, ay + ah],
                "shape2_id": shape2["id"],
                "shape2_label": _label(shape2),
                "shape2_bounds": [bx, by, bx + bw, by + bh],
                "overlap_area": [ox1, oy1, ox2, oy2],
                "cause": cause,
                "suggestion": _overlap_suggestion(
                    shape1, shape2, ax, ay, aw, ah, bx, by, bw, bh
                ),
                "fix": _build_node_overlap_fix(
                    shape2, ax, ay, aw, ah, bx, by, bw, bh
                ),
            }
            if cause == "label_overflow":
                entry["shape1_render_bounds"] = [rax, ray, rax + raw, ray + rah]
                entry["shape2_render_bounds"] = [rbx, rby, rbx + rbw, rby + rbh]
            node_overlaps.append(entry)

    # -----------------------------------------------------------------------
    # 2.  Out-of-container boundary violations
    # -----------------------------------------------------------------------
    out_of_container: list[dict] = []
    for shape in vertices:
        pid = shape.get("parent")
        if not pid or pid in _DEFAULT_ROOT_IDS:
            continue  # top-level shape — no container to check
        if pid not in abs_bounds:
            continue  # parent not a known vertex

        cx, cy, cw, ch = abs_bounds[pid]
        sx, sy, sw, sh = abs_bounds[shape["id"]]

        if sw <= 0 or sh <= 0:
            continue

        container = cells_by_id.get(pid, {})
        style = (shape.get("style") or "").lower()
        if _is_uml_section(style):
            continue

        if not _box_contains(cx, cy, cw, ch, sx, sy, sw, sh):
            out_of_container.append({
                "shape_id": shape["id"],
                "shape_label": _label(shape),
                "shape_bounds": [sx, sy, sx + sw, sy + sh],
                "container_id": pid,
                "container_label": _label(container),
                "container_bounds": [cx, cy, cx + cw, cy + ch],
                "suggestion": _containment_suggestion(shape, container, sx, sy, sw, sh, cx, cy, cw, ch),
                "fix": _build_containment_fix(
                    shape, container, sx, sy, sw, sh, cx, cy, cw, ch
                ),
            })

    return {
        "node_overlaps": node_overlaps,
        "out_of_container": out_of_container,
        "label_overlaps": _detect_label_overlaps(cells, abs_bounds),
    }


# ---------------------------------------------------------------------------
# Label overlap detection
# ---------------------------------------------------------------------------

# Match the label-size heuristic used by diagram.Diagram when placing labels.
# Kept for backwards compatibility; new code should call render_geometry's
# ``edge_label_rect`` which is font-size aware.
_LABEL_CHAR_WIDTH = 3.5
_LABEL_H_PADDING = 6.0
_LABEL_LINE_HEIGHT = 7.0
_LABEL_MIN_HALF_W = 20.0
_LABEL_MIN_HALF_H = 8.0


def _strip_html(text: str) -> str:
    # Convert <br> and block breaks to newlines, then drop remaining tags.
    t = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    t = re.sub(r"</(div|p|li|tr|h[1-6])>", "\n", t, flags=re.IGNORECASE)
    t = re.sub(r"<[^>]+>", "", t)
    return t


def _estimate_label_half_size(label: str) -> tuple[float, float]:
    """Estimate (half_width, half_height) of a rendered label box.

    Legacy heuristic kept for callers that still expect it.  New code should
    prefer ``render_geometry.edge_label_rect`` which is font-size aware.
    """
    plain = _strip_html(label or "").strip()
    if not plain:
        return _LABEL_MIN_HALF_W, _LABEL_MIN_HALF_H
    lines = plain.split("\n")
    longest = max(len(line) for line in lines) if lines else 0
    half_w = max(_LABEL_MIN_HALF_W, longest * _LABEL_CHAR_WIDTH + _LABEL_H_PADDING)
    half_h = max(_LABEL_MIN_HALF_H, len(lines) * _LABEL_LINE_HEIGHT)
    return half_w, half_h


def _edge_endpoint(
    connection: dict,
    shape_id: str,
    attr_prefix: str,
    shapes_bounds: dict[str, tuple[float, float, float, float]],
    fallback_point_key: str,
) -> Optional[tuple[float, float]]:
    """Return the absolute (x, y) anchor for one end of an edge."""
    if shape_id and shape_id in shapes_bounds:
        x, y, w, h = shapes_bounds[shape_id]
        try:
            fx = float(connection.get(f"{attr_prefix}_x", 0.5))
            fy = float(connection.get(f"{attr_prefix}_y", 0.5))
        except (TypeError, ValueError):
            fx, fy = 0.5, 0.5
        return (x + w * fx, y + h * fy)
    point = connection.get(fallback_point_key)
    if point and len(point) >= 2:
        try:
            return (float(point[0]), float(point[1]))
        except (TypeError, ValueError):
            return None
    return None


def _edge_label_anchor(
    connection: dict,
    shapes_bounds: dict[str, tuple[float, float, float, float]],
) -> Optional[tuple[float, float]]:
    """Approximate where Draw.io will anchor the edge label on its polyline."""
    start = _edge_endpoint(
        connection, connection.get("source"), "exit", shapes_bounds, "source_point"
    )
    end = _edge_endpoint(
        connection, connection.get("target"), "entry", shapes_bounds, "target_point"
    )
    if start is None or end is None:
        return None

    path: list[tuple[float, float]] = [start]
    for wp in connection.get("waypoints", []) or []:
        if isinstance(wp, (list, tuple)) and len(wp) >= 2:
            try:
                path.append((float(wp[0]), float(wp[1])))
            except (TypeError, ValueError):
                pass
    path.append(end)

    seg_lengths: list[float] = []
    total = 0.0
    for i in range(len(path) - 1):
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        length = (dx * dx + dy * dy) ** 0.5
        seg_lengths.append(length)
        total += length
    if total <= 0:
        return path[0]

    half = total / 2.0
    travelled = 0.0
    for i, length in enumerate(seg_lengths):
        if travelled + length >= half:
            t = (half - travelled) / length if length else 0.0
            return (
                path[i][0] + t * (path[i + 1][0] - path[i][0]),
                path[i][1] + t * (path[i + 1][1] - path[i][1]),
            )
        travelled += length
    return path[-1]


def _detect_label_overlaps(
    cells: list[dict],
    abs_bounds: dict[str, tuple[float, float, float, float]],
) -> list[dict]:
    """Detect edge-label overlaps against nodes, other edge labels, and edges."""
    shapes_by_id = {c["id"]: c for c in cells if c.get("vertex")}
    edges = [c for c in cells if c.get("edge")]

    # Collect label rects for every labelled edge, using font-aware sizing.
    edge_labels: list[dict] = []
    for edge in edges:
        label = (edge.get("value") or "").strip()
        if not label:
            continue
        anchor = _edge_label_anchor(edge, abs_bounds)
        if anchor is None:
            continue
        ox = _safe_float(edge.get("label_offset_x"), 0.0)
        oy = _safe_float(edge.get("label_offset_y"), 0.0)
        style_dict = parse_style(edge.get("style") or "")
        has_bg = bool(style_dict.get("labelbackgroundcolor"))
        rect = edge_label_rect(
            anchor,
            label,
            edge.get("style") or "",
            label_offset_x=ox,
            label_offset_y=oy,
            has_background=has_bg,
        )
        edge_labels.append({
            "edge_id": edge["id"],
            "label": _label(edge),
            "rect": rect,
            "source": edge.get("source"),
            "target": edge.get("target"),
        })

    # Pre-compute every edge's polyline segments once for the
    # label↔edge-path collision pass below.
    edge_segments: list[tuple[str, str, list[tuple[tuple[float, float], tuple[float, float]]]]] = []
    for edge in edges:
        segs = _edge_segments(edge, abs_bounds)
        if segs:
            edge_segments.append((edge["id"], _label(edge), segs))

    overlaps: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()

    # 1. edge label ↔ unrelated node body
    for info in edge_labels:
        lr = info["rect"]
        exclude = {info["source"], info["target"]}
        for shape_id, shape in shapes_by_id.items():
            if shape_id in exclude:
                continue
            if _is_uml_section((shape.get("style") or "").lower()):
                continue
            if shape_id not in abs_bounds:
                continue
            sx, sy, sw, sh = abs_bounds[shape_id]
            if sw <= 0 or sh <= 0:
                continue
            if _boxes_overlap(lr[0], lr[1], lr[2], lr[3], sx, sy, sw, sh):
                pair = (info["edge_id"], shape_id)
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                overlaps.append({
                    "issue_type": "edge_label_over_node",
                    "edge_id": info["edge_id"],
                    "edge_label": info["label"],
                    "node_id": shape_id,
                    "node_label": _label(shape),
                    "label_bounds": [lr[0], lr[1], lr[0] + lr[2], lr[1] + lr[3]],
                    "node_bounds": [sx, sy, sx + sw, sy + sh],
                    "suggestion": (
                        f"Edge label '{info['label']}' overlaps node '{_label(shape)}'. "
                        "Adjust the connection's label_offset_x/label_offset_y to push the "
                        "label clear of the node, or reroute the connection with waypoints."
                    ),
                    "fix": _build_label_clear_fix(info, lr, [(sx, sy, sw, sh)]),
                })

    # 2. edge label ↔ edge label
    for i, a in enumerate(edge_labels):
        for b in edge_labels[i + 1:]:
            ax, ay, aw, ah = a["rect"]
            bx, by, bw, bh = b["rect"]
            if _boxes_overlap(ax, ay, aw, ah, bx, by, bw, bh):
                overlaps.append({
                    "issue_type": "edge_label_over_edge_label",
                    "edge_id": a["edge_id"],
                    "edge_label": a["label"],
                    "other_edge_id": b["edge_id"],
                    "other_edge_label": b["label"],
                    "label_bounds": [ax, ay, ax + aw, ay + ah],
                    "other_label_bounds": [bx, by, bx + bw, by + bh],
                    "suggestion": (
                        f"Labels '{a['label']}' and '{b['label']}' overlap. "
                        "Set distinct label_offset_x/label_offset_y on one of the "
                        "connections or route the edges along different paths."
                    ),
                    "fix": _build_label_clear_fix(a, a["rect"], [b["rect"]]),
                })

    # 3. edge label ↔ another edge's path (text crossing a line is also ugly).
    for info in edge_labels:
        lr = info["rect"]
        for other_id, other_label, segs in edge_segments:
            if other_id == info["edge_id"]:
                continue
            crosses = any(segment_intersects_rect(s1, s2, lr) for s1, s2 in segs)
            if not crosses:
                continue
            pair = ("path", info["edge_id"], other_id)
            key = (pair[1], pair[2])
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            overlaps.append({
                "issue_type": "edge_label_over_edge_path",
                "edge_id": info["edge_id"],
                "edge_label": info["label"],
                "other_edge_id": other_id,
                "other_edge_label": other_label,
                "label_bounds": [lr[0], lr[1], lr[0] + lr[2], lr[1] + lr[3]],
                "suggestion": (
                    f"Edge label '{info['label']}' sits on top of the "
                    f"connection '{other_label}'. Push the label aside via "
                    "label_offset_x/label_offset_y, or reroute one of the edges."
                ),
                "fix": {
                    "op": "update_cell",
                    "args": {
                        "cell_id": info["edge_id"],
                        "label_offset_y": max(20.0, lr[3]),
                    },
                    "rationale": "Push the label vertically off the crossing edge.",
                },
            })

    return overlaps


def _edge_segments(
    edge: dict,
    abs_bounds: dict[str, tuple[float, float, float, float]],
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Return ordered segments for an edge as a polyline."""
    start = _edge_endpoint(edge, edge.get("source"), "exit", abs_bounds, "source_point")
    end = _edge_endpoint(edge, edge.get("target"), "entry", abs_bounds, "target_point")
    if start is None or end is None:
        return []
    points: list[tuple[float, float]] = [start]
    for wp in edge.get("waypoints") or []:
        if isinstance(wp, (list, tuple)) and len(wp) >= 2:
            try:
                points.append((float(wp[0]), float(wp[1])))
            except (TypeError, ValueError):
                continue
    points.append(end)
    return [
        (points[i], points[i + 1])
        for i in range(len(points) - 1)
        if points[i] != points[i + 1]
    ]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _label(cell: dict) -> str:
    """Return a human-readable label for a cell."""
    raw = (cell.get("value") or "").strip()
    # Strip HTML tags for display
    plain = re.sub(r"<[^>]+>", "", raw).strip()
    return plain or cell.get("id", "(unknown)")


def _is_uml_section(style: str) -> bool:
    """Heuristic: return True if the style belongs to a UML class sub-section cell.

    See ``crossing_detector._is_uml_section``: only the ``portConstraint=eastwest``
    marker is authoritative; the former ``line;...;strokeWidth`` fallback produced
    false positives for ordinary line shapes.
    """
    return "portconstraint=eastwest" in style


def _overlap_suggestion(
    shape1: dict, shape2: dict,
    ax: float, ay: float, aw: float, ah: float,
    bx: float, by: float, bw: float, bh: float,
) -> str:
    """Generate a fix suggestion for an overlapping pair."""
    label1 = _label(shape1)
    label2 = _label(shape2)

    # Suggest the minimum move needed to separate the two boxes
    # (move shape2 — since it appears second in iteration order)
    overlap_w = min(ax + aw, bx + bw) - max(ax, bx)
    overlap_h = min(ay + ah, by + bh) - max(ay, by)

    lines = [
        f"'{label1}' and '{label2}' overlap.",
        f"  '{label1}' bounds: ({ax:.0f}, {ay:.0f}) → ({ax + aw:.0f}, {ay + ah:.0f})",
        f"  '{label2}' bounds: ({bx:.0f}, {by:.0f}) → ({bx + bw:.0f}, {by + bh:.0f})",
        f"  Overlap region: width={overlap_w:.0f}px, height={overlap_h:.0f}px",
        "  Suggested fixes (choose one):",
    ]

    # Prefer moving horizontally or vertically based on smaller gap
    gap = 20  # minimum desired gap after separation
    if overlap_w <= overlap_h:
        # Separate horizontally
        if bx >= ax:
            new_bx = ax + aw + gap
            lines.append(f"  1. Move '{label2}' right: new_x={new_bx:.0f} (current x={bx:.0f})")
        else:
            new_bx = ax - bw - gap
            lines.append(f"  1. Move '{label2}' left: new_x={new_bx:.0f} (current x={bx:.0f})")
    else:
        # Separate vertically
        if by >= ay:
            new_by = ay + ah + gap
            lines.append(f"  1. Move '{label2}' down: new_y={new_by:.0f} (current y={by:.0f})")
        else:
            new_by = ay - bh - gap
            lines.append(f"  1. Move '{label2}' up: new_y={new_by:.0f} (current y={by:.0f})")

    lines.append(f"  2. Resize '{label1}' or '{label2}' to reduce their footprint")
    lines.append(f"  3. Rearrange layout so nodes do not share the same area")
    return "\n".join(lines)


def _containment_suggestion(
    shape: dict, container: dict,
    sx: float, sy: float, sw: float, sh: float,
    cx: float, cy: float, cw: float, ch: float,
) -> str:
    """Generate a fix suggestion for a shape that escapes its container."""
    slabel = _label(shape)
    clabel = _label(container)

    # Calculate how far out the shape extends
    over_right = max(0.0, (sx + sw) - (cx + cw))
    over_bottom = max(0.0, (sy + sh) - (cy + ch))
    over_left = max(0.0, cx - sx)
    over_top = max(0.0, cy - sy)

    lines = [
        f"'{slabel}' (bounds: ({sx:.0f},{sy:.0f})→({sx+sw:.0f},{sy+sh:.0f})) "
        f"extends outside its container '{clabel}' "
        f"(bounds: ({cx:.0f},{cy:.0f})→({cx+cw:.0f},{cy+ch:.0f})).",
    ]

    fixes = []
    if over_right > 0:
        lines.append(f"  Overflows right by {over_right:.0f}px")
        # Move shape left so it fits, or expand container right
        new_sx = cx + cw - sw - 10
        fixes.append(
            f"  a) Move '{slabel}' left inside container: new relative_x ≈ {new_sx - cx:.0f}"
        )
        fixes.append(
            f"     OR expand '{clabel}' width to at least {sx + sw - cx + 10:.0f}px"
        )
    if over_bottom > 0:
        lines.append(f"  Overflows bottom by {over_bottom:.0f}px")
        new_sy = cy + ch - sh - 10
        fixes.append(
            f"  b) Move '{slabel}' up inside container: new relative_y ≈ {new_sy - cy:.0f}"
        )
        fixes.append(
            f"     OR expand '{clabel}' height to at least {sy + sh - cy + 10:.0f}px"
        )
    if over_left > 0:
        lines.append(f"  Overflows left by {over_left:.0f}px")
        fixes.append(f"  c) Move '{slabel}' right inside container: new relative_x ≈ 10")
        fixes.append(
            f"     OR move '{clabel}' left so its x ≤ {sx - 10:.0f}"
        )
    if over_top > 0:
        lines.append(f"  Overflows top by {over_top:.0f}px")
        fixes.append(f"  d) Move '{slabel}' down inside container: new relative_y ≈ 10")
        fixes.append(
            f"     OR move '{clabel}' up so its y ≤ {sy - 10:.0f}"
        )

    if fixes:
        lines.append("  Suggested fixes:")
        lines.extend(fixes)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Structured fix builders (Req 2)
# ---------------------------------------------------------------------------

def _build_node_overlap_fix(
    shape2: dict,
    ax: float, ay: float, aw: float, ah: float,
    bx: float, by: float, bw: float, bh: float,
    gap: float = 20.0,
) -> dict:
    """Compute a minimum-displacement move for ``shape2`` away from shape1.

    Returns a ``{"op": "move_shape", "args": {...}, "rationale": str}``
    descriptor that an AI / the batch handler can execute verbatim.
    """
    overlap_w = max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    overlap_h = max(0.0, min(ay + ah, by + bh) - max(ay, by))

    # `shape2` x/y in the *model* may be relative to its parent — read the
    # stored raw x/y rather than the absolute bx/by, and translate.
    try:
        raw_x = float(shape2.get("x") or 0)
        raw_y = float(shape2.get("y") or 0)
    except (TypeError, ValueError):
        raw_x, raw_y = bx, by

    # Prefer the axis with the smaller overlap (minimum displacement).
    if overlap_w <= overlap_h:
        if bx >= ax:
            dx = (ax + aw + gap) - bx
        else:
            dx = (ax - bw - gap) - bx
        new_x = raw_x + dx
        new_y = raw_y
        direction = "right" if dx > 0 else "left"
    else:
        if by >= ay:
            dy = (ay + ah + gap) - by
        else:
            dy = (ay - bh - gap) - by
        new_x = raw_x
        new_y = raw_y + dy
        direction = "down" if dy > 0 else "up"

    return {
        "op": "move_shape",
        "args": {
            "shape_id": shape2["id"],
            "new_x": new_x,
            "new_y": new_y,
        },
        "rationale": (
            f"Move '{shape2.get('id')}' {direction} so it no longer overlaps "
            f"(minimum separation + {gap:.0f}px gap)."
        ),
    }


def _build_containment_fix(
    shape: dict, container: dict,
    sx: float, sy: float, sw: float, sh: float,
    cx: float, cy: float, cw: float, ch: float,
    margin: float = 10.0,
) -> dict:
    """Return a ``move_shape`` fix that places the shape inside its container.

    Uses the same relative-coordinate semantics that Draw.io does: children
    of a container store ``(x, y)`` relative to the container's own origin.
    """
    # Clamp absolute position so the cell fits with a margin inside container.
    tx = min(max(sx, cx + margin), max(cx + margin, cx + cw - sw - margin))
    ty = min(max(sy, cy + margin), max(cy + margin, cy + ch - sh - margin))
    # Translate back into "relative-to-container" coordinates (drawio stores
    # child x/y as relative offsets from the parent origin).
    new_rel_x = tx - cx
    new_rel_y = ty - cy
    return {
        "op": "move_shape",
        "args": {
            "shape_id": shape["id"],
            "new_x": new_rel_x,
            "new_y": new_rel_y,
        },
        "rationale": (
            f"Move '{shape.get('id')}' to relative ({new_rel_x:.0f}, "
            f"{new_rel_y:.0f}) so it fits inside '{container.get('id')}' "
            f"with a {margin:.0f}px margin."
        ),
    }


def _build_label_clear_fix(
    edge_info: dict,
    label_rect: tuple[float, float, float, float],
    obstacles: list[tuple[float, float, float, float]],
    margin: float = 8.0,
) -> dict:
    """Return an ``update_cell`` fix that nudges the label clear of obstacles.

    Picks the axis-aligned shift with the smallest magnitude that clears
    *all* obstacles. Falls back to "push down" when no obstacle exists.
    """
    lx, ly, lw, lh = label_rect
    cx = lx + lw / 2.0
    cy = ly + lh / 2.0

    candidates: list[tuple[float, float]] = [(0.0, 0.0)]
    for rx, ry, rw, rh in obstacles:
        # Up: top of label above top of obstacle
        candidates.append((0.0, (ry - lh / 2.0 - margin) - cy))
        # Down
        candidates.append((0.0, (ry + rh + lh / 2.0 + margin) - cy))
        # Left
        candidates.append(((rx - lw / 2.0 - margin) - cx, 0.0))
        # Right
        candidates.append(((rx + rw + lw / 2.0 + margin) - cx, 0.0))

    def clears(dx: float, dy: float) -> bool:
        sx, sy = lx + dx, ly + dy
        for rx, ry, rw, rh in obstacles:
            if sx < rx + rw and rx < sx + lw and sy < ry + rh and ry < sy + lh:
                return False
        return True

    clearing = [(dx, dy) for dx, dy in candidates if (dx, dy) != (0.0, 0.0) and clears(dx, dy)]
    if clearing:
        dx, dy = min(clearing, key=lambda d: d[0] ** 2 + d[1] ** 2)
    else:
        # Nothing clears cleanly — push straight down by one label height.
        dx, dy = 0.0, lh + margin

    # Combine with any existing offset baked into the label's absolute rect.
    # The label rect already includes the previous offset, so we only emit the
    # delta as an *absolute* value to replace the old offset.
    return {
        "op": "update_cell",
        "args": {
            "cell_id": edge_info["edge_id"],
            "label_offset_x": round(dx, 2),
            "label_offset_y": round(dy, 2),
        },
        "rationale": (
            f"Offset label on edge '{edge_info['edge_id']}' by "
            f"({dx:.0f}, {dy:.0f}) to clear its obstacles."
        ),
    }
