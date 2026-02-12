#!/usr/bin/env python3
"""
Demo: UML Class Diagram Support

This demo showcases the new UML class diagram capabilities of the MCP Draw.io Server.
It creates a complete class diagram for a simple library management system.
"""

import tempfile
import os
from mcp_drawio_server.diagram import Diagram


def create_library_management_uml():
    """Create a UML class diagram for a library management system"""
    print("\n=== Creating Library Management System UML Class Diagram ===\n")
    
    diagram = Diagram("Library Management System")
    
    # Package container
    package = diagram.add_shape(
        "library.management",
        x=30, y=30,
        width=740, height=550,
        shape_type="uml_package"
    )
    
    # Core classes
    book = diagram.add_shape(
        "Book\n───────────\n- isbn: String\n- title: String\n- author: String\n- year: int\n- available: boolean\n───────────\n+ getInfo(): String\n+ isAvailable(): boolean\n+ setAvailable(bool)",
        x=50, y=80,
        width=200, height=180,
        shape_type="uml_class"
    )
    
    member = diagram.add_shape(
        "Member\n───────────\n- id: int\n- name: String\n- email: String\n- joinDate: Date\n───────────\n+ borrowBook(Book)\n+ returnBook(Book)\n+ getHistory(): List",
        x=300, y=80,
        width=200, height=180,
        shape_type="uml_class"
    )
    
    loan = diagram.add_shape(
        "Loan\n───────────\n- id: int\n- book: Book\n- member: Member\n- loanDate: Date\n- returnDate: Date\n───────────\n+ calculateFee(): decimal\n+ isOverdue(): boolean",
        x=550, y=80,
        width=200, height=180,
        shape_type="uml_class"
    )
    
    # Abstract base class
    user = diagram.add_shape(
        "User\n───────────\n- username: String\n- password: String\n───────────\n+ login(): boolean\n+ logout(): void",
        x=170, y=320,
        width=200, height=140,
        shape_type="uml_abstract_class"
    )
    
    librarian = diagram.add_shape(
        "Librarian\n───────────\n- employeeId: String\n───────────\n+ addBook(Book)\n+ removeBook(Book)\n+ processLoan(Loan)",
        x=50, y=500,
        width=200, height=140,
        shape_type="uml_class"
    )
    
    # Interface
    searchable = diagram.add_shape(
        "«interface»\nSearchable\n───────────\n+ search(query): List\n+ filter(criteria): List",
        x=420, y=320,
        width=200, height=100,
        shape_type="uml_interface"
    )
    
    # Enum
    book_status = diagram.add_shape(
        "«enumeration»\nBookStatus\n───────────\nAVAILABLE\nLOANED\nREPAIR\nLOST",
        x=420, y=460,
        width=150, height=140,
        shape_type="uml_enum"
    )
    
    # Note
    note = diagram.add_shape(
        "The system manages books,\nmembers, and loans.\nLibrarians can perform\nadministrative tasks.",
        x=600, y=480,
        width=150, height=100,
        shape_type="uml_note"
    )
    
    # Add relationships
    # Loan has Book (association)
    diagram.add_connection(
        loan, book,
        label="has",
        style="endArrow=open;endSize=12;"
    )
    
    # Loan has Member (association)
    diagram.add_connection(
        loan, member,
        label="has",
        style="endArrow=open;endSize=12;"
    )
    
    # Member borrows many Books (association)
    diagram.add_connection(
        member, book,
        label="borrows *",
        style="endArrow=open;endSize=12;"
    )
    
    # Member extends User (inheritance)
    diagram.add_connection(
        member, user,
        label="",
        style="endArrow=block;endFill=0;endSize=12;"
    )
    
    # Librarian extends User (inheritance)
    diagram.add_connection(
        librarian, user,
        label="",
        style="endArrow=block;endFill=0;endSize=12;"
    )
    
    # Book implements Searchable (realization)
    diagram.add_connection(
        book, searchable,
        label="",
        style="endArrow=block;dashed=1;endFill=0;endSize=12;"
    )
    
    # Book uses BookStatus (dependency)
    diagram.add_connection(
        book, book_status,
        label="uses",
        style="endArrow=open;dashed=1;endSize=12;"
    )
    
    # Generate and save
    xml = diagram.to_drawio_xml()
    
    print(f"✓ Created UML class diagram with:")
    print(f"  - {len(diagram.shapes)} shapes")
    print(f"  - {len(diagram.connections)} relationships")
    print(f"  - 1 package")
    print(f"  - 5 classes")
    print(f"  - 1 abstract class")
    print(f"  - 1 interface")
    print(f"  - 1 enumeration")
    print(f"  - 1 note")
    print()
    
    # List relationships
    print("Relationships:")
    print("  - Inheritance: Member → User")
    print("  - Inheritance: Librarian → User")
    print("  - Realization: Book → Searchable")
    print("  - Association: Member ↔ Book")
    print("  - Association: Loan → Book")
    print("  - Association: Loan → Member")
    print("  - Dependency: Book → BookStatus")
    
    return xml


def create_simple_animal_hierarchy():
    """Create a simple inheritance hierarchy example"""
    print("\n=== Creating Animal Hierarchy UML Diagram ===\n")
    
    diagram = Diagram("Animal Hierarchy")
    
    # Abstract base class
    animal = diagram.add_shape(
        "Animal\n───────────\n# name: String\n# age: int\n───────────\n+ getName(): String\n+ makeSound(): void",
        x=250, y=50,
        width=180, height=140,
        shape_type="uml_abstract_class"
    )
    
    # Concrete classes
    dog = diagram.add_shape(
        "Dog\n───────────\n- breed: String\n───────────\n+ bark(): void\n+ makeSound(): void",
        x=80, y=250,
        width=160, height=120,
        shape_type="uml_class"
    )
    
    cat = diagram.add_shape(
        "Cat\n───────────\n- indoor: boolean\n───────────\n+ meow(): void\n+ makeSound(): void",
        x=280, y=250,
        width=160, height=120,
        shape_type="uml_class"
    )
    
    bird = diagram.add_shape(
        "Bird\n───────────\n- canFly: boolean\n───────────\n+ chirp(): void\n+ makeSound(): void",
        x=480, y=250,
        width=160, height=120,
        shape_type="uml_class"
    )
    
    # Interface
    pet_interface = diagram.add_shape(
        "«interface»\nPet\n───────────\n+ play(): void\n+ feed(): void",
        x=300, y=420,
        width=140, height=80,
        shape_type="uml_interface"
    )
    
    # Add inheritance relationships
    diagram.add_connection(
        dog, animal,
        label="",
        style="endArrow=block;endFill=0;endSize=12;"
    )
    
    diagram.add_connection(
        cat, animal,
        label="",
        style="endArrow=block;endFill=0;endSize=12;"
    )
    
    diagram.add_connection(
        bird, animal,
        label="",
        style="endArrow=block;endFill=0;endSize=12;"
    )
    
    # Implement Pet interface
    diagram.add_connection(
        dog, pet_interface,
        label="",
        style="endArrow=block;dashed=1;endFill=0;endSize=12;"
    )
    
    diagram.add_connection(
        cat, pet_interface,
        label="",
        style="endArrow=block;dashed=1;endFill=0;endSize=12;"
    )
    
    xml = diagram.to_drawio_xml()
    
    print(f"✓ Created animal hierarchy with:")
    print(f"  - 1 abstract class (Animal)")
    print(f"  - 3 concrete classes (Dog, Cat, Bird)")
    print(f"  - 1 interface (Pet)")
    print(f"  - 5 relationships")
    
    return xml


if __name__ == "__main__":
    print("=" * 60)
    print("UML Class Diagram Demo")
    print("=" * 60)
    
    # Get temp directory for cross-platform compatibility
    temp_dir = tempfile.gettempdir()
    
    # Create library management system diagram
    library_xml = create_library_management_uml()
    library_path = os.path.join(temp_dir, "demo_library_uml.drawio")
    with open(library_path, "w") as f:
        f.write(library_xml)
    print(f"\n✓ Saved to: {library_path}")
    
    # Create animal hierarchy diagram
    animal_xml = create_simple_animal_hierarchy()
    animal_path = os.path.join(temp_dir, "demo_animal_hierarchy_uml.drawio")
    with open(animal_path, "w") as f:
        f.write(animal_xml)
    print(f"\n✓ Saved to: {animal_path}")
    
    print("\n" + "=" * 60)
    print("✓ Demo completed successfully!")
    print("=" * 60)
    print("\nOpen the .drawio files in:")
    print("  - VS Code with Draw.io extension")
    print("  - Draw.io desktop application")
    print("  - https://app.diagrams.net/")
    print()
