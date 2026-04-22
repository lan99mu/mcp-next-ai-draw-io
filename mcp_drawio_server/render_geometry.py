"""
Render-geometry helpers shared by overlap/crossing detection, label placement,
and the auto-layout algorithm.

Goals (see Requirement 4):
    * Estimate text bounding boxes from real font metrics (font_size, bold,
      CJK awareness) instead of a single hard-coded character width.
    * Provide a shape ``render_bounds`` that unions the cell bounds with the
      bounding box of the label as Draw.io would render it (taking
      ``align`` / ``verticalAlign`` / ``overflow=visible`` into account).
    * Provide an edge-label rectangle helper that adds padding when a
      label_background_color is set.

All functions are pure: they take cell dictionaries (as returned by
``xml_operations.get_cells_from_xml``) plus already-resolved absolute bounds
and return new tuples / dicts.  No global state, no I/O.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Optional


# ---------------------------------------------------------------------------
# Font metric heuristics
# ---------------------------------------------------------------------------

# Average glyph width relative to font_size for ASCII / narrow characters.
_ASCII_WIDTH_RATIO = 0.55
# Bold glyphs are roughly 10% wider.
_BOLD_WIDTH_BONUS = 1.10
# CJK / fullwidth glyphs are square — width ≈ font_size.
_CJK_WIDTH_RATIO = 1.00
# Browsers render text with ~1.2× line-height by default.
_LINE_HEIGHT_RATIO = 1.2

# Inner padding when Draw.io renders a label inside a shape (px on each side).
_DEFAULT_LABEL_PADDING_X = 6.0
_DEFAULT_LABEL_PADDING_Y = 4.0
# Floor for very short / empty labels so a small reserved area still exists.
_MIN_LABEL_WIDTH = 12.0
_MIN_LABEL_HEIGHT = 12.0
# Padding around an edge label when a background colour is present.
_LABEL_BG_PADDING = 3.0


_HTML_LINE_BREAK_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_HTML_BLOCK_BREAK_RE = re.compile(
    r"</(?:div|p|li|tr|h[1-6])\s*>|<(?:br|hr)\s*/?>", re.IGNORECASE
)
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    """Convert an HTML label into visible plain text for sizing calculations."""
    if not text:
        return ""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _HTML_LINE_BREAK_RE.sub("\n", normalized)
    normalized = _HTML_BLOCK_BREAK_RE.sub("\n", normalized)
    normalized = _HTML_TAG_RE.sub("", normalized)
    # NB: we deliberately don't run html.unescape here; entity widths are close
    # enough to their literal forms that the extra dependency on stdlib's
    # ``html`` module is unnecessary for sizing.
    return normalized.strip("\n")


def _line_visual_width(line: str, font_size: float, bold: bool) -> float:
    """Estimate the rendered width (px) of a single line of text."""
    if not line:
        return 0.0
    base = font_size * _ASCII_WIDTH_RATIO
    cjk = font_size * _CJK_WIDTH_RATIO
    width = 0.0
    for ch in line:
        if unicodedata.east_asian_width(ch) in {"W", "F"}:
            width += cjk
        else:
            width += base
    if bold:
        width *= _BOLD_WIDTH_BONUS
    return width


def estimate_text_bounds(
    text: str,
    font_size: float = 12.0,
    bold: bool = False,
) -> tuple[float, float]:
    """Return ``(width, height)`` of the rendered text block in pixels.

    Args:
        text: Label text (HTML or plain).  ``<br>``/``\\n`` are treated as
            line breaks.
        font_size: Font size in pixels.  Falls back to 12 when 0/None.
        bold: Whether the text is rendered bold.

    Returns:
        A tuple ``(width, height)``.  Both are at least one font-size's
        worth so callers don't end up with a zero-area rectangle when the
        label is empty.
    """
    if not font_size or font_size <= 0:
        font_size = 12.0
    plain = _strip_html(text)
    lines = plain.split("\n") if plain else [""]
    width = max((_line_visual_width(line, font_size, bold) for line in lines), default=0.0)
    height = len(lines) * font_size * _LINE_HEIGHT_RATIO
    width = max(width, _MIN_LABEL_WIDTH)
    height = max(height, _MIN_LABEL_HEIGHT)
    return width, height


# ---------------------------------------------------------------------------
# Style parsing helpers
# ---------------------------------------------------------------------------

def parse_style(style: str) -> dict[str, str]:
    """Parse a Draw.io style string into a key→value dict.

    Tokens without ``=`` (the leading shape selector e.g. ``ellipse``) are
    stored under their own name with an empty value.
    """
    result: dict[str, str] = {}
    if not style:
        return result
    for token in style.split(";"):
        token = token.strip()
        if not token:
            continue
        if "=" in token:
            k, _, v = token.partition("=")
            result[k.strip().lower()] = v.strip()
        else:
            result[token.lower()] = ""
    return result


def style_font_size(style_dict: dict[str, str], default: float = 12.0) -> float:
    """Return the fontSize in px from a parsed style dict, else ``default``."""
    raw = style_dict.get("fontsize")
    if not raw:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def style_is_bold(style_dict: dict[str, str]) -> bool:
    """Draw.io encodes fontStyle as a bitmask: 1=bold, 2=italic, 4=underline."""
    raw = style_dict.get("fontstyle", "")
    try:
        return bool(int(raw) & 1)
    except (TypeError, ValueError):
        return False


def style_overflow_visible(style_dict: dict[str, str]) -> bool:
    """Return True when text is allowed to escape the shape's bounding box."""
    overflow = style_dict.get("overflow", "").lower()
    return overflow == "visible"


def style_align(style_dict: dict[str, str]) -> tuple[str, str]:
    """Return ``(align, verticalAlign)`` with sensible defaults."""
    align = style_dict.get("align", "center").lower()
    valign = style_dict.get("verticalalign", "middle").lower()
    return align, valign


# ---------------------------------------------------------------------------
# Shape render bounds
# ---------------------------------------------------------------------------

def shape_label_box(
    cell_bounds: tuple[float, float, float, float],
    label: str,
    style: str,
    padding_x: float = _DEFAULT_LABEL_PADDING_X,
    padding_y: float = _DEFAULT_LABEL_PADDING_Y,
) -> tuple[float, float, float, float]:
    """Compute the absolute (x, y, w, h) of a shape's label box.

    Honours the shape's ``align`` / ``verticalAlign`` to position the label
    relative to the cell.  When ``overflow=visible``, the label can extend
    outside the cell bounds; otherwise it is clipped to them.
    """
    x, y, w, h = cell_bounds
    sd = parse_style(style or "")
    fs = style_font_size(sd)
    bold = style_is_bold(sd)
    tw, th = estimate_text_bounds(label, fs, bold)
    tw += 2 * padding_x
    th += 2 * padding_y

    align, valign = style_align(sd)
    overflow_visible = style_overflow_visible(sd)

    # Horizontal positioning of the label box.
    if align == "left":
        lx = x
    elif align == "right":
        lx = x + w - tw
    else:  # center
        lx = x + (w - tw) / 2.0

    # Vertical positioning.
    if valign == "top":
        ly = y
    elif valign == "bottom":
        ly = y + h - th
    else:  # middle
        ly = y + (h - th) / 2.0

    if not overflow_visible:
        # Clip to the cell bounds.
        lx = max(lx, x)
        ly = max(ly, y)
        right = min(lx + tw, x + w)
        bottom = min(ly + th, y + h)
        tw = max(0.0, right - lx)
        th = max(0.0, bottom - ly)
    return lx, ly, tw, th


def shape_render_bounds(
    cell_bounds: tuple[float, float, float, float],
    label: str,
    style: str,
) -> tuple[float, float, float, float]:
    """Return the union of the cell and the label box (when label overflows).

    Always covers the cell itself.  When ``overflow=visible`` and the label
    is longer / taller than the cell, the returned rectangle expands
    accordingly.  This is what overlap detection should compare against
    so that long labels escaping a 'visible' cell are detected as
    overlapping their neighbours.
    """
    x, y, w, h = cell_bounds
    if w <= 0 or h <= 0:
        return cell_bounds
    sd = parse_style(style or "")
    if not style_overflow_visible(sd):
        return cell_bounds
    lx, ly, lw, lh = shape_label_box(cell_bounds, label, style)
    if lw <= 0 or lh <= 0:
        return cell_bounds
    nx = min(x, lx)
    ny = min(y, ly)
    nx2 = max(x + w, lx + lw)
    ny2 = max(y + h, ly + lh)
    return nx, ny, nx2 - nx, ny2 - ny


# ---------------------------------------------------------------------------
# Edge label rectangle
# ---------------------------------------------------------------------------

def edge_label_rect(
    anchor: tuple[float, float],
    label: str,
    style: str,
    label_offset_x: float = 0.0,
    label_offset_y: float = 0.0,
    has_background: bool = False,
) -> tuple[float, float, float, float]:
    """Return the absolute ``(x, y, w, h)`` of an edge label.

    ``anchor`` is the polyline midpoint (already-resolved absolute coords).
    ``has_background`` adds extra padding to mirror the visual area of the
    background rectangle Draw.io draws when a labelBackgroundColor is set.
    """
    sd = parse_style(style or "")
    fs = style_font_size(sd, default=11.0)  # edge labels default to 11px
    bold = style_is_bold(sd)
    tw, th = estimate_text_bounds(label, fs, bold)
    if has_background:
        tw += 2 * _LABEL_BG_PADDING
        th += 2 * _LABEL_BG_PADDING
    cx = anchor[0] + label_offset_x
    cy = anchor[1] + label_offset_y
    return cx - tw / 2.0, cy - th / 2.0, tw, th


# ---------------------------------------------------------------------------
# Generic geometry helpers (re-exported for callers that don't want to depend
# on numpy / shapely).
# ---------------------------------------------------------------------------

def boxes_overlap(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> bool:
    """Standard AABB intersection test."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def box_intersection(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> Optional[tuple[float, float, float, float]]:
    """Return the (x, y, w, h) of the intersection rectangle, or None."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1 = max(ax, bx)
    y1 = max(ay, by)
    x2 = min(ax + aw, bx + bw)
    y2 = min(ay + ah, by + bh)
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2 - x1, y2 - y1


def segment_intersects_rect(
    p1: tuple[float, float],
    p2: tuple[float, float],
    rect: tuple[float, float, float, float],
) -> bool:
    """Return True when the segment p1→p2 crosses the rectangle interior.

    Liang–Barsky parametric clipping; identical to the implementation in
    ``crossing_detector`` and ``diagram`` but exposed here for re-use.
    """
    rx, ry, rw, rh = rect
    if rw <= 0 or rh <= 0:
        return False
    x1, y1 = p1
    x2, y2 = p2
    # Endpoint inside?
    if rx < x1 < rx + rw and ry < y1 < ry + rh:
        return True
    if rx < x2 < rx + rw and ry < y2 < ry + rh:
        return True
    dx = x2 - x1
    dy = y2 - y1
    t_enter = 0.0
    t_exit = 1.0
    for p, q in (
        (-dx, x1 - rx),
        (dx, rx + rw - x1),
        (-dy, y1 - ry),
        (dy, ry + rh - y1),
    ):
        if abs(p) < 1e-12:
            if q < 0:
                return False
            continue
        t = q / p
        if p < 0:
            if t > t_exit:
                return False
            if t > t_enter:
                t_enter = t
        else:
            if t < t_enter:
                return False
            if t < t_exit:
                t_exit = t
    return t_exit - t_enter > 1e-9


__all__ = [
    "estimate_text_bounds",
    "parse_style",
    "style_font_size",
    "style_is_bold",
    "style_overflow_visible",
    "style_align",
    "shape_label_box",
    "shape_render_bounds",
    "edge_label_rect",
    "boxes_overlap",
    "box_intersection",
    "segment_intersects_rect",
]
