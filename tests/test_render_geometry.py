"""Tests for font-aware text measurement & render-bounds (Requirement 4)."""

from mcp_drawio_server.render_geometry import (
    edge_label_rect,
    estimate_text_bounds,
    shape_render_bounds,
    parse_style,
    style_is_bold,
    style_overflow_visible,
    boxes_overlap,
)


def test_estimate_text_bounds_scales_with_font_size():
    small_w, small_h = estimate_text_bounds("Hello", font_size=10)
    big_w, big_h = estimate_text_bounds("Hello", font_size=30)
    assert big_w > small_w * 2
    assert big_h > small_h * 2


def test_cjk_glyph_wider_than_ascii():
    ascii_w, _ = estimate_text_bounds("abcde", font_size=14)
    cjk_w, _ = estimate_text_bounds("你好世界字", font_size=14)
    # 5 CJK chars should be markedly wider than 5 ASCII chars at same font size.
    assert cjk_w > ascii_w * 1.5


def test_bold_widens_text():
    plain_w, _ = estimate_text_bounds("hello world", font_size=14, bold=False)
    bold_w, _ = estimate_text_bounds("hello world", font_size=14, bold=True)
    assert bold_w > plain_w


def test_multiline_label_grows_vertically():
    one_w, one_h = estimate_text_bounds("single", font_size=14)
    three_w, three_h = estimate_text_bounds("a<br>b<br>c", font_size=14)
    assert three_h >= one_h * 2.5
    # width for the 3-line block is based on its widest line "a" — should be
    # no greater than a same-font single-line label of similar length.
    assert three_w <= max(one_w, estimate_text_bounds("abcde", 14)[0])


def test_shape_render_bounds_returns_cell_when_overflow_hidden():
    cell = (100.0, 50.0, 80.0, 40.0)
    rb = shape_render_bounds(cell, "a very very very long label", "whiteSpace=wrap;html=1;")
    # overflow=hidden (default) -> render bounds == cell bounds
    assert rb == cell


def test_shape_render_bounds_expands_when_overflow_visible():
    cell = (100.0, 50.0, 40.0, 20.0)
    rb = shape_render_bounds(cell, "A really really really long label", "overflow=visible;")
    # Label is wider than 40px; render bounds must extend horizontally.
    assert rb[2] > cell[2]


def test_edge_label_rect_adds_padding_for_background():
    no_bg = edge_label_rect((100, 100), "label", "fontSize=11;", has_background=False)
    with_bg = edge_label_rect((100, 100), "label", "fontSize=11;", has_background=True)
    assert with_bg[2] > no_bg[2]
    assert with_bg[3] > no_bg[3]


def test_parse_style_and_flags():
    sd = parse_style("rounded=0;fontSize=16;fontStyle=1;overflow=visible;html=1;")
    assert sd["fontsize"] == "16"
    assert style_is_bold(sd)
    assert style_overflow_visible(sd)


def test_boxes_overlap_basic():
    a = (0.0, 0.0, 10.0, 10.0)
    b = (5.0, 5.0, 10.0, 10.0)
    c = (20.0, 20.0, 5.0, 5.0)
    assert boxes_overlap(a, b)
    assert not boxes_overlap(a, c)
