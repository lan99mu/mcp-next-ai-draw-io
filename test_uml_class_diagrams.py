#!/usr/bin/env python3
"""
Test UML Class Diagram Support

This test demonstrates creating UML class diagrams with the new shape types.
"""

from mcp_drawio_server.diagram import Diagram


def test_uml_class_diagram():
    """Test creating a UML class diagram"""
    print("\n=== Testing UML Class Diagram Creation ===\n")
    
    diagram = Diagram("UML Class Diagram Test")
    
    # Create a simple class diagram
    # Main class
    person_class = diagram.add_shape(
        "Person",
        x=100, y=50,
        width=160, height=100,
        shape_type="uml_class"
    )
    
    # Abstract class
    animal_class = diagram.add_shape(
        "Animal",
        x=100, y=200,
        width=160, height=100,
        shape_type="uml_abstract_class"
    )
    
    # Interface
    drawable_interface = diagram.add_shape(
        "«interface»\nDrawable",
        x=320, y=50,
        width=160, height=80,
        shape_type="uml_interface"
    )
    
    # Enum
    color_enum = diagram.add_shape(
        "«enumeration»\nColor",
        x=320, y=200,
        width=140, height=100,
        shape_type="uml_enum"
    )
    
    # Package
    models_package = diagram.add_shape(
        "models",
        x=50, y=350,
        width=450, height=200,
        shape_type="uml_package"
    )
    
    # UML Note
    note = diagram.add_shape(
        "This is a UML class diagram\ndemonstrating various shapes",
        x=550, y=50,
        width=200, height=80,
        shape_type="uml_note"
    )
    
    # Add connections
    # Inheritance (Person inherits from Animal)
    diagram.add_connection(
        person_class, animal_class,
        label="",
        style="endArrow=block;endFill=0;endSize=12;"
    )
    
    # Interface implementation (Person implements Drawable)
    diagram.add_connection(
        person_class, drawable_interface,
        label="",
        style="endArrow=block;dashed=1;endFill=0;endSize=12;"
    )
    
    # Association (Person uses Color)
    diagram.add_connection(
        person_class, color_enum,
        label="uses",
        style="endArrow=open;endSize=12;"
    )
    
    # Generate XML
    xml = diagram.to_drawio_xml()
    
    # Verify the diagram contains UML shapes
    assert 'Person' in xml
    assert 'Animal' in xml
    assert 'Drawable' in xml
    assert 'Color' in xml
    assert 'models' in xml
    
    # Verify shape types are present
    assert diagram.shapes[person_class].shape_type == "uml_class"
    assert diagram.shapes[animal_class].shape_type == "uml_abstract_class"
    assert diagram.shapes[drawable_interface].shape_type == "uml_interface"
    assert diagram.shapes[color_enum].shape_type == "uml_enum"
    assert diagram.shapes[models_package].shape_type == "uml_package"
    assert diagram.shapes[note].shape_type == "uml_note"
    
    print("✓ UML class diagram created successfully")
    print(f"  - Created {len(diagram.shapes)} shapes")
    print(f"  - Created {len(diagram.connections)} connections")
    print(f"  - Shapes: uml_class, uml_abstract_class, uml_interface, uml_enum, uml_package, uml_note")
    
    return xml


def test_comprehensive_uml_diagram():
    """Test creating a more comprehensive UML class diagram"""
    print("\n=== Testing Comprehensive UML Class Diagram ===\n")
    
    diagram = Diagram("E-Commerce System")
    
    # Create multiple classes
    user_class = diagram.add_shape(
        "User\n───────\n- id: int\n- name: string\n- email: string\n───────\n+ login()\n+ logout()",
        x=50, y=50,
        width=180, height=140,
        shape_type="uml_class"
    )
    
    customer_class = diagram.add_shape(
        "Customer\n───────\n- address: string\n───────\n+ placeOrder()",
        x=50, y=250,
        width=180, height=100,
        shape_type="uml_class"
    )
    
    product_class = diagram.add_shape(
        "Product\n───────\n- id: int\n- name: string\n- price: decimal\n───────\n+ getPrice()",
        x=300, y=50,
        width=180, height=140,
        shape_type="uml_class"
    )
    
    order_class = diagram.add_shape(
        "Order\n───────\n- id: int\n- date: datetime\n───────\n+ calculate()",
        x=300, y=250,
        width=180, height=100,
        shape_type="uml_class"
    )
    
    # Interface for payment
    payment_interface = diagram.add_shape(
        "«interface»\nPaymentProcessor\n───────\n+ processPayment()",
        x=550, y=150,
        width=180, height=80,
        shape_type="uml_interface"
    )
    
    # Add relationships
    # Inheritance: Customer extends User
    diagram.add_connection(
        customer_class, user_class,
        label="",
        style="endArrow=block;endFill=0;endSize=12;"
    )
    
    # Association: Customer places Orders
    diagram.add_connection(
        customer_class, order_class,
        label="places",
        style="endArrow=open;endSize=12;"
    )
    
    # Association: Order contains Products
    diagram.add_connection(
        order_class, product_class,
        label="contains",
        style="endArrow=open;endSize=12;"
    )
    
    # Dependency: Order uses PaymentProcessor
    diagram.add_connection(
        order_class, payment_interface,
        label="uses",
        style="endArrow=open;dashed=1;endSize=12;"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify the comprehensive diagram
    assert 'User' in xml
    assert 'Customer' in xml
    assert 'Product' in xml
    assert 'Order' in xml
    assert 'PaymentProcessor' in xml
    
    print("✓ Comprehensive UML class diagram created successfully")
    print(f"  - Created {len(diagram.shapes)} classes/interfaces")
    print(f"  - Created {len(diagram.connections)} relationships")
    print(f"  - Demonstrated inheritance, association, and dependency")
    
    return xml


def test_all_uml_shapes():
    """Test all UML class diagram shape types"""
    print("\n=== Testing All UML Shape Types ===\n")
    
    diagram = Diagram("UML Shape Types Test")
    
    uml_shapes = [
        "uml_class",
        "uml_interface",
        "uml_abstract_class",
        "uml_enum",
        "uml_package",
        "uml_note"
    ]
    
    y_position = 50
    for i, shape_type in enumerate(uml_shapes):
        shape_id = diagram.add_shape(
            label=shape_type.replace("_", " ").title(),
            x=100,
            y=y_position,
            width=200,
            height=80,
            shape_type=shape_type
        )
        y_position += 120
        
        # Verify shape type
        assert diagram.shapes[shape_id].shape_type == shape_type
    
    xml = diagram.to_drawio_xml()
    
    # Verify all shape types are in the XML
    for shape_type in uml_shapes:
        label = shape_type.replace("_", " ").title()
        assert label in xml
    
    print(f"✓ Successfully created all {len(uml_shapes)} UML shape types")
    for shape_type in uml_shapes:
        print(f"  - {shape_type}")
    
    return xml


if __name__ == "__main__":
    print("Testing UML Class Diagram Support")
    print("=" * 50)
    
    # Run tests
    xml1 = test_uml_class_diagram()
    xml2 = test_comprehensive_uml_diagram()
    xml3 = test_all_uml_shapes()
    
    print("\n" + "=" * 50)
    print("✓ All UML class diagram tests passed!")
    print("=" * 50)
    
    # Save examples
    with open("uml_class_diagram_test.drawio", "w") as f:
        f.write(xml1)
    print("\n✓ Saved example diagram to: uml_class_diagram_test.drawio")
    
    with open("uml_comprehensive_test.drawio", "w") as f:
        f.write(xml2)
    print("✓ Saved comprehensive diagram to: uml_comprehensive_test.drawio")
    
    with open("uml_all_shapes_test.drawio", "w") as f:
        f.write(xml3)
    print("✓ Saved all shapes test to: uml_all_shapes_test.drawio")
