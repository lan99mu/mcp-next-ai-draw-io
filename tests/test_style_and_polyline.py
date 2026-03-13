#!/usr/bin/env python3
"""
Test Style and Polyline Support

Tests for new style options (dashed, rounded, colors) and polyline connections.
"""

from mcp_drawio_server.diagram import Diagram


def test_shape_dashed_border():
    """Test creating a shape with dashed border."""
    diagram = Diagram("Dashed Border Test")
    
    shape_id = diagram.add_shape(
        label="Dashed Shape",
        x=100, y=100,
        width=120, height=60,
        dashed=True
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify dashed style is applied
    assert "dashed=1" in xml
    assert "Dashed Shape" in xml
    
    # Verify shape was created correctly
    assert shape_id in diagram.shapes
    assert diagram.shapes[shape_id].dashed is True


def test_shape_rounded_corners():
    """Test creating a shape with rounded corners."""
    diagram = Diagram("Rounded Corners Test")
    
    shape_id = diagram.add_shape(
        label="Rounded Shape",
        x=100, y=100,
        width=120, height=60,
        rounded=True
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify rounded style is applied
    assert "rounded=1" in xml
    assert "Rounded Shape" in xml


def test_shape_custom_colors():
    """Test creating a shape with custom colors."""
    diagram = Diagram("Custom Colors Test")
    
    shape_id = diagram.add_shape(
        label="Colored Shape",
        x=100, y=100,
        width=120, height=60,
        fill_color="#e1f5ff",
        stroke_color="#0077cc",
        font_color="#333333"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify color styles are applied
    assert "fillColor=#e1f5ff" in xml
    assert "strokeColor=#0077cc" in xml
    assert "fontColor=#333333" in xml


def test_shape_stroke_width():
    """Test creating a shape with custom stroke width."""
    diagram = Diagram("Stroke Width Test")
    
    shape_id = diagram.add_shape(
        label="Thick Border",
        x=100, y=100,
        width=120, height=60,
        stroke_width=3
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify stroke width is applied
    assert "strokeWidth=3" in xml


def test_shape_combined_styles():
    """Test creating a shape with multiple style options."""
    diagram = Diagram("Combined Styles Test")
    
    shape_id = diagram.add_shape(
        label="Combined Styles",
        x=100, y=100,
        width=150, height=80,
        dashed=True,
        rounded=True,
        stroke_width=2,
        fill_color="#ffe6e6",
        stroke_color="#cc0000",
        font_size=14,
        opacity=80
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify all styles are applied
    assert "dashed=1" in xml
    assert "rounded=1" in xml
    assert "strokeWidth=2" in xml
    assert "fillColor=#ffe6e6" in xml
    assert "strokeColor=#cc0000" in xml
    assert "fontSize=14" in xml
    assert "opacity=80" in xml


def test_connection_dashed_line():
    """Test creating a connection with dashed line."""
    diagram = Diagram("Dashed Connection Test")
    
    shape1 = diagram.add_shape("Source", x=100, y=100)
    shape2 = diagram.add_shape("Target", x=300, y=100)
    
    conn_id = diagram.add_connection(
        source_id=shape1,
        target_id=shape2,
        label="Dashed Link",
        dashed=True
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify dashed style is applied to connection
    assert "dashed=1" in xml
    assert diagram.connections[conn_id].dashed is True


def test_connection_rounded_orthogonal():
    """Test creating an orthogonal connection with rounded corners."""
    diagram = Diagram("Rounded Connection Test")
    
    shape1 = diagram.add_shape("Source", x=100, y=100)
    shape2 = diagram.add_shape("Target", x=300, y=300)
    
    conn_id = diagram.add_connection(
        source_id=shape1,
        target_id=shape2,
        edge_style="orthogonal",
        rounded=True
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify rounded orthogonal style
    assert "rounded=1" in xml
    assert "orthogonal" in xml.lower() or "edgestyle" in xml.lower()


def test_connection_straight_edge():
    """Test creating a straight (non-orthogonal) connection."""
    diagram = Diagram("Straight Edge Test")
    
    shape1 = diagram.add_shape("Source", x=100, y=100)
    shape2 = diagram.add_shape("Target", x=300, y=300)
    
    conn_id = diagram.add_connection(
        source_id=shape1,
        target_id=shape2,
        edge_style="straight"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify straight edge style
    assert "edgeStyle=none" in xml
    assert diagram.connections[conn_id].edge_style == "straight"


def test_connection_curved_edge():
    """Test creating a curved connection."""
    diagram = Diagram("Curved Edge Test")
    
    shape1 = diagram.add_shape("Source", x=100, y=100)
    shape2 = diagram.add_shape("Target", x=300, y=300)
    
    conn_id = diagram.add_connection(
        source_id=shape1,
        target_id=shape2,
        edge_style="curved"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify curved edge style
    assert "curved=1" in xml
    assert diagram.connections[conn_id].edge_style == "curved"


def test_connection_with_waypoints():
    """Test creating a polyline connection with waypoints."""
    diagram = Diagram("Waypoints Test")
    
    shape1 = diagram.add_shape("Source", x=100, y=100, width=100, height=50)
    shape2 = diagram.add_shape("Target", x=400, y=300, width=100, height=50)
    
    # Create a polyline with two bend points
    conn_id = diagram.add_connection(
        source_id=shape1,
        target_id=shape2,
        waypoints=[(200, 125), (200, 325), (350, 325)]
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify waypoints are in the XML
    assert '<Array as="points">' in xml
    assert '<mxPoint x="200" y="125"/>' in xml
    assert '<mxPoint x="200" y="325"/>' in xml
    assert '<mxPoint x="350" y="325"/>' in xml
    
    # Verify waypoints stored in connection
    assert len(diagram.connections[conn_id].waypoints) == 3


def test_connection_start_and_end_arrows():
    """Test creating a connection with both start and end arrows."""
    diagram = Diagram("Bidirectional Arrows Test")
    
    shape1 = diagram.add_shape("A", x=100, y=100)
    shape2 = diagram.add_shape("B", x=300, y=100)
    
    conn_id = diagram.add_connection(
        source_id=shape1,
        target_id=shape2,
        start_arrow="classic",
        end_arrow="block"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify both arrows are in the style
    assert "startArrow=classic" in xml
    assert "endArrow=block" in xml


def test_connection_stroke_style():
    """Test creating a connection with custom stroke width and color."""
    diagram = Diagram("Stroke Style Test")
    
    shape1 = diagram.add_shape("Source", x=100, y=100)
    shape2 = diagram.add_shape("Target", x=300, y=100)
    
    conn_id = diagram.add_connection(
        source_id=shape1,
        target_id=shape2,
        stroke_width=3,
        stroke_color="#ff0000"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify stroke styles are applied
    assert "strokeWidth=3" in xml
    assert "strokeColor=#ff0000" in xml


def test_uml_inheritance_dashed():
    """Test UML interface implementation (dashed with hollow arrow)."""
    diagram = Diagram("UML Inheritance Test")
    
    interface = diagram.add_shape(
        "«interface»\nIService",
        x=100, y=50,
        width=160, height=80,
        shape_type="uml_interface"
    )
    
    impl_class = diagram.add_shape(
        "ServiceImpl",
        x=100, y=200,
        width=160, height=80,
        shape_type="uml_class"
    )
    
    # Implementation relationship (dashed with block arrow)
    conn_id = diagram.add_connection(
        source_id=impl_class,
        target_id=interface,
        dashed=True,
        end_arrow="block",
        start_arrow="none"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify UML inheritance style
    assert "dashed=1" in xml
    assert "endArrow=block" in xml


def test_auto_size_calculation():
    """Test auto-size calculation for shapes."""
    diagram = Diagram("Auto Size Test")
    
    # Short text - should use minimum size
    short_id = diagram.add_shape(
        label="Hi",
        x=100, y=100,
        auto_size=True
    )
    
    # Multi-line text - should be taller
    multi_line_id = diagram.add_shape(
        label="Line 1\nLine 2\nLine 3\nLine 4",
        x=100, y=200,
        auto_size=True
    )
    
    # Long text - should be wider
    long_id = diagram.add_shape(
        label="This is a very long label that should make the shape wider",
        x=100, y=350,
        auto_size=True
    )
    
    # Verify auto-sizing was applied
    # Multi-line should be taller than short
    assert diagram.shapes[multi_line_id].height > diagram.shapes[short_id].height
    # Long text should be wider
    assert diagram.shapes[long_id].width > 120  # Default is 120


def test_labels_are_exported_as_html_for_shapes_and_connections():
    """All shape and connection labels should use Draw.io HTML label formatting."""
    diagram = Diagram("HTML Label Test")

    source_id = diagram.add_shape(
        label="Title\n<div>Body</div>",
        x=100, y=100
    )
    target_id = diagram.add_shape(
        label="Target",
        x=320, y=100
    )
    diagram.add_connection(
        source_id=source_id,
        target_id=target_id,
        label="Line 1\n<b>Bold</b>"
    )

    xml = diagram.to_drawio_xml()

    assert 'Title&lt;br&gt;&lt;div&gt;Body&lt;/div&gt;' in xml
    assert 'Line 1&lt;br&gt;&lt;b&gt;Bold&lt;/b&gt;' in xml


def test_auto_size_expands_custom_dimensions_and_ignores_html_tags():
    """Auto-size should expand past custom minimums using visible text, not raw HTML tags."""
    diagram = Diagram("HTML Auto Size Test")

    html_id = diagram.add_shape(
        label="Short <b>wide</b>",
        x=100, y=100,
        width=60,
        height=20,
        auto_size=True
    )
    multi_line_id = diagram.add_shape(
        label="<div>Line 1</div><div>Line 2</div>",
        x=100, y=200,
        width=60,
        height=20,
        auto_size=True
    )

    html_shape = diagram.shapes[html_id]
    multi_line_shape = diagram.shapes[multi_line_id]

    assert 100 <= html_shape.width < 140
    assert html_shape.height > 20
    assert multi_line_shape.height > html_shape.height


def test_parent_child_relationship():
    """Test parent-child container relationship."""
    diagram = Diagram("Parent Child Test")
    
    # Create a container
    container_id = diagram.add_shape(
        label="Container",
        x=50, y=50,
        width=300, height=200,
        shape_type="container"
    )
    
    # Create a child shape inside the container
    child_id = diagram.add_shape(
        label="Child",
        x=20, y=30,  # Relative to container
        width=80, height=40,
        parent_id=container_id
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify parent relationship in XML
    assert f'parent="{container_id}"' in xml
    assert diagram.shapes[child_id].parent_id == container_id


def test_add_uml_class_helper():
    """Test the add_uml_class helper method."""
    diagram = Diagram("UML Class Helper Test")
    
    # Create a UML class using the helper
    result = diagram.add_uml_class(
        name="User",
        attributes=["- id: int", "- name: string", "- email: string"],
        methods=["+ login()", "+ logout()", "+ getProfile()"],
        x=100, y=100,
        width=180
    )
    
    assert "class_id" in result
    assert result["class_id"] in diagram.shapes
    
    shape = diagram.shapes[result["class_id"]]
    assert shape.shape_type == "uml_class"
    assert "User" in shape.label
    # Attributes and methods are now stored in uml_sections, not in label
    assert len(shape.uml_sections) >= 2  # At least attributes section and methods section
    # Verify attributes are in a section
    attr_content = "\n".join(s.content for s in shape.uml_sections if s.section_type == "text")
    assert "- id: int" in attr_content
    assert "+ login()" in attr_content
    # Height should be auto-calculated
    assert shape.height > 100  # Should be larger due to content


def test_add_uml_class_interface():
    """Test the add_uml_class helper for interfaces."""
    diagram = Diagram("UML Interface Helper Test")
    
    result = diagram.add_uml_class(
        name="«interface»\nIService",
        methods=["+ execute()", "+ validate()"],
        x=100, y=100,
        class_type="interface"
    )
    
    shape = diagram.shapes[result["class_id"]]
    assert shape.shape_type == "uml_interface"
    assert "IService" in shape.label
    # Methods are now stored in uml_sections, not in label
    method_content = "\n".join(s.content for s in shape.uml_sections if s.section_type == "text")
    assert "+ execute()" in method_content


def test_add_swimlane_pool():
    """Test the add_swimlane_pool helper method."""
    diagram = Diagram("Swimlane Pool Test")
    
    result = diagram.add_swimlane_pool(
        name="Order Process",
        lanes=["Customer", "Sales", "Warehouse"],
        x=50, y=50,
        pool_width=700,
        lane_height=150
    )
    
    assert "pool_id" in result
    assert "lane_ids" in result
    assert len(result["lane_ids"]) == 3
    
    # Verify pool was created
    pool = diagram.shapes[result["pool_id"]]
    assert pool.shape_type == "swimlane_pool"
    assert pool.label == "Order Process"
    
    # Verify lanes were created with parent relationship
    for lane_id in result["lane_ids"]:
        lane = diagram.shapes[lane_id]
        assert lane.parent_id == result["pool_id"]
    
    # Verify bindings
    assert len(pool.bound_nodes) == 3  # Bound to all 3 lanes


def test_bind_shapes_helper():
    """Test the bind_shapes helper method."""
    diagram = Diagram("Bind Shapes Test")
    
    shape1 = diagram.add_shape("A", x=100, y=100)
    shape2 = diagram.add_shape("B", x=200, y=100)
    shape3 = diagram.add_shape("C", x=300, y=100)
    
    # Bind the shapes
    diagram.bind_shapes([shape1, shape2, shape3])
    
    # Verify all shapes are bound to each other
    assert shape2 in diagram.shapes[shape1].bound_nodes
    assert shape3 in diagram.shapes[shape1].bound_nodes
    assert shape1 in diagram.shapes[shape2].bound_nodes
    assert shape3 in diagram.shapes[shape2].bound_nodes
    assert shape1 in diagram.shapes[shape3].bound_nodes
    assert shape2 in diagram.shapes[shape3].bound_nodes


if __name__ == "__main__":
    print("Testing Style and Polyline Support")
    print("=" * 50)
    
    # Run all tests
    test_shape_dashed_border()
    print("✓ test_shape_dashed_border passed")
    
    test_shape_rounded_corners()
    print("✓ test_shape_rounded_corners passed")
    
    test_shape_custom_colors()
    print("✓ test_shape_custom_colors passed")
    
    test_shape_stroke_width()
    print("✓ test_shape_stroke_width passed")
    
    test_shape_combined_styles()
    print("✓ test_shape_combined_styles passed")
    
    test_connection_dashed_line()
    print("✓ test_connection_dashed_line passed")
    
    test_connection_rounded_orthogonal()
    print("✓ test_connection_rounded_orthogonal passed")
    
    test_connection_straight_edge()
    print("✓ test_connection_straight_edge passed")
    
    test_connection_curved_edge()
    print("✓ test_connection_curved_edge passed")
    
    test_connection_with_waypoints()
    print("✓ test_connection_with_waypoints passed")
    
    test_connection_start_and_end_arrows()
    print("✓ test_connection_start_and_end_arrows passed")
    
    test_connection_stroke_style()
    print("✓ test_connection_stroke_style passed")
    
    test_uml_inheritance_dashed()
    print("✓ test_uml_inheritance_dashed passed")
    
    test_auto_size_calculation()
    print("✓ test_auto_size_calculation passed")
    
    test_parent_child_relationship()
    print("✓ test_parent_child_relationship passed")
    
    test_add_uml_class_helper()
    print("✓ test_add_uml_class_helper passed")
    
    test_add_uml_class_interface()
    print("✓ test_add_uml_class_interface passed")
    
    test_add_swimlane_pool()
    print("✓ test_add_swimlane_pool passed")
    
    test_bind_shapes_helper()
    print("✓ test_bind_shapes_helper passed")
    
    print("\n" + "=" * 50)
    print("✓ All style and polyline tests passed!")
    print("=" * 50)
