# UML Class Diagram Examples

This document demonstrates how to create UML class diagrams using the MCP Draw.io Server.

## New UML Shape Types

The following UML class diagram shape types are now supported:

- `uml_class` - Standard UML class with compartments
- `uml_interface` - Interface (displayed with italic header)
- `uml_abstract_class` - Abstract class (displayed with italic text)
- `uml_enum` - Enumeration
- `uml_package` - Package/namespace container
- `uml_note` - UML note/comment

## Example 1: Basic Class Diagram

```python
from mcp_drawio_server.diagram import Diagram

# Create diagram
diagram = Diagram("Simple Class Diagram")

# Add a class
person_class = diagram.add_shape(
    "Person\n───────\n- name: string\n- age: int\n───────\n+ getName()\n+ getAge()",
    x=100, y=50,
    width=160, height=140,
    shape_type="uml_class"
)

# Add an interface
drawable = diagram.add_shape(
    "«interface»\nDrawable\n───────\n+ draw()",
    x=300, y=50,
    width=160, height=100,
    shape_type="uml_interface"
)

# Add inheritance relationship
diagram.add_connection(
    person_class, drawable,
    style="endArrow=block;dashed=1;endFill=0;endSize=12;"
)

# Save to file
xml = diagram.to_drawio_xml()
with open("class_diagram.drawio", "w") as f:
    f.write(xml)
```

## Example 2: E-Commerce System

```python
# Create a more comprehensive example
diagram = Diagram("E-Commerce System")

# Create classes
user = diagram.add_shape(
    "User\n───────\n- id: int\n- email: string\n───────\n+ login()\n+ logout()",
    x=50, y=50, width=180, height=120,
    shape_type="uml_class"
)

customer = diagram.add_shape(
    "Customer\n───────\n- address: string\n───────\n+ placeOrder()",
    x=50, y=220, width=180, height=100,
    shape_type="uml_class"
)

product = diagram.add_shape(
    "Product\n───────\n- id: int\n- name: string\n- price: decimal",
    x=300, y=50, width=180, height=100,
    shape_type="uml_class"
)

order = diagram.add_shape(
    "Order\n───────\n- id: int\n- date: datetime\n───────\n+ calculate()",
    x=300, y=220, width=180, height=100,
    shape_type="uml_class"
)

# Add interface
payment = diagram.add_shape(
    "«interface»\nPaymentProcessor\n───────\n+ process()",
    x=550, y=150, width=180, height=80,
    shape_type="uml_interface"
)

# Add relationships
# Inheritance: Customer extends User
diagram.add_connection(
    customer, user,
    style="endArrow=block;endFill=0;endSize=12;"
)

# Association: Customer places Orders
diagram.add_connection(
    customer, order,
    label="places",
    style="endArrow=open;endSize=12;"
)

# Association: Order contains Products
diagram.add_connection(
    order, product,
    label="contains",
    style="endArrow=open;endSize=12;"
)

# Dependency: Order uses PaymentProcessor
diagram.add_connection(
    order, payment,
    label="uses",
    style="endArrow=open;dashed=1;endSize=12;"
)
```

## Example 3: Using All UML Shapes

```python
diagram = Diagram("UML Shape Types")

# Class
cls = diagram.add_shape(
    "MyClass\n───────\n- field: int\n───────\n+ method()",
    x=50, y=50, width=150, height=100,
    shape_type="uml_class"
)

# Interface
intf = diagram.add_shape(
    "«interface»\nMyInterface\n───────\n+ operation()",
    x=250, y=50, width=150, height=80,
    shape_type="uml_interface"
)

# Abstract Class
abstract = diagram.add_shape(
    "AbstractBase\n───────\n+ abstract method()",
    x=450, y=50, width=150, height=80,
    shape_type="uml_abstract_class"
)

# Enum
enum = diagram.add_shape(
    "«enumeration»\nStatus\n───────\nACTIVE\nINACTIVE\nPENDING",
    x=50, y=200, width=150, height=120,
    shape_type="uml_enum"
)

# Package
package = diagram.add_shape(
    "com.example.models",
    x=250, y=200, width=350, height=150,
    shape_type="uml_package"
)

# Note
note = diagram.add_shape(
    "This is an explanatory note\nabout the design",
    x=50, y=380, width=200, height=60,
    shape_type="uml_note"
)
```

## UML Relationship Styles

### Inheritance (Generalization)
```python
# Solid line with hollow arrow
style="endArrow=block;endFill=0;endSize=12;"
```

### Interface Implementation (Realization)
```python
# Dashed line with hollow arrow
style="endArrow=block;dashed=1;endFill=0;endSize=12;"
```

### Association
```python
# Solid line with open arrow
style="endArrow=open;endSize=12;"
```

### Dependency
```python
# Dashed line with open arrow
style="endArrow=open;dashed=1;endSize=12;"
```

### Composition
```python
# Solid line with filled diamond
style="endArrow=diamondThin;endFill=1;endSize=12;"
```

### Aggregation
```python
# Solid line with hollow diamond
style="endArrow=diamondThin;endFill=0;endSize=12;"
```

## Tips for Creating UML Class Diagrams

1. **Use proper formatting**: Separate class name, attributes, and methods with lines (───────)
2. **Mark visibility**: Use +/- for public/private members
3. **Label stereotypes**: Use «interface», «enumeration», «abstract» etc.
4. **Choose appropriate relationships**: Use the correct arrow style for the relationship type
5. **Group related classes**: Use packages to organize classes

## Supported Label Formats

The MCP Draw.io Server supports two UML class label formats:

### Format 1: Box-Drawing Style (Recommended)
Use Unicode box-drawing characters (─) to separate sections:

```
"ClassName\n───────\n- field1: type\n- field2: type\n───────\n+ method1()\n+ method2()"
```

### Format 2: Pipe-Separated Style (GraphViz/Mermaid Compatible)
Use `|` as section separators and `\l` for line breaks within sections:

```
"ClassName|+ field1: type\l+ field2: type\l|+ method1()\l+ method2()\l"
```

Example with both formats producing the same result:
```python
# Format 1 - Box-drawing style
label1 = "Teacher\n───────\n+ id: string\n+ name: string\n───────\n+ teach(): void"

# Format 2 - Pipe-separated style  
label2 = r"Teacher|+ id: string\l+ name: string\l|+ teach(): void\l"

# Both create the same UML class structure in Draw.io
```

## Using with MCP Tools

When using the MCP server, you can create UML class diagrams like this:

```
User: "Create a UML class diagram for a simple blog system with User, Post, and Comment classes"

Copilot will:
1. Call create_diagram with name "Blog System"
2. Call add_shape for each class with shape_type="uml_class"
3. Call add_connection for relationships (inheritance, associations)
4. Call save_diagram to save the result
```

The UML shapes will be properly formatted and ready to open in Draw.io!
