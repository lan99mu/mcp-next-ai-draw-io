# Example Usage

This document provides examples of how to use the MCP Draw.io Server with AI assistants.

## Example 1: Simple Flowchart

**Prompt to AI:**
```
Using the Draw.io MCP server, create a simple flowchart for making coffee:
1. Start
2. Check if we have coffee beans (decision)
3. If no, buy coffee beans
4. If yes, grind beans
5. Brew coffee
6. End

Position the shapes nicely with appropriate spacing.
```

**Expected AI Actions:**
1. Creates a new diagram named "Coffee Making Process"
2. Adds shapes for each step
3. Connects them with arrows
4. Returns the Draw.io XML

## Example 2: System Architecture

**Prompt to AI:**
```
Create a system architecture diagram showing:
- Client (browser) at the top
- Load Balancer below it
- Three API Servers in a row
- Database at the bottom
- Cache server to the side
Connect them appropriately.
```

**Expected Result:**
A multi-tier architecture diagram with all components connected.

## Example 3: ER Diagram

**Prompt to AI:**
```
Create an entity-relationship diagram for a simple blog:
- User entity (with attributes: id, username, email)
- Post entity (with attributes: id, title, content)
- Comment entity (with attributes: id, text)
- Category entity (with attributes: id, name)

Show the relationships:
- User has many Posts
- Post has many Comments
- User has many Comments
- Post belongs to many Categories
```

## Example 4: Process Flow

**Prompt to AI:**
```
Create a business process diagram for order fulfillment:
1. Receive Order (parallelogram)
2. Check Inventory (diamond)
3. If in stock: Process Payment (rectangle)
4. If not in stock: Reorder Stock (rectangle)
5. Ship Order (rectangle)
6. Update Database (cylinder)
7. Send Confirmation (cloud)
```

## Working with the Output

After the AI generates the diagram:

1. **Save the XML output** to a file:
   ```bash
   # Save the XML content to a file
   echo '<mxfile>...</mxfile>' > my_diagram.drawio
   ```

2. **Open in VS Code**:
   - Install the Draw.io Integration extension
   - Open the `.drawio` file
   - Edit and refine as needed

3. **Open in Draw.io**:
   - Go to https://app.diagrams.net/
   - File → Open → Select your `.drawio` file
   - Or use the Draw.io desktop application

## Tips for Better Diagrams

1. **Specify positions**: Give x, y coordinates for better layout
   ```
   Place the first shape at (100, 50), the second at (300, 50)...
   ```

2. **Use appropriate shape types**:
   - Rectangles for processes
   - Diamonds for decisions
   - Parallelograms for input/output
   - Cylinders for databases
   - Clouds for cloud services

3. **Add labels**: Always label your shapes and connections clearly

4. **Specify arrow types**: Use different arrow types to show different relationships

5. **Organize hierarchically**: Place related elements near each other

## Advanced: Custom Styles

You can specify custom Draw.io styles to use ANY shape from Draw.io's extensive library:

### Example 5: Using Custom Draw.io Shapes

**Prompt to AI:**
```
Create a system diagram using custom Draw.io shapes:
- User (UML actor shape): style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
- Web Server (server rack): style="shape=cube;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;"
- Database (datastore): style="shape=datastore;whiteSpace=wrap;html=1;"
- Cloud Storage (cloud with AWS style): style="sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=#ffffff;"
```

### Example 6: Network Diagram with Icons

**Prompt to AI:**
```
Create a network diagram with these shapes:
- Router: style="shape=mxgraph.cisco.routers.router;html=1;"
- Switch: style="shape=mxgraph.cisco.switches.workgroup_switch;html=1;"
- Firewall: style="shape=mxgraph.cisco.security.firewall;html=1;"
- Server: style="shape=mxgraph.cisco.servers.server;html=1;"
```

### How to Find Style Strings

1. Open Draw.io (https://app.diagrams.net/)
2. Create or select the shape you want
3. Right-click → Edit Style (or press Ctrl+E / Cmd+E)
4. Copy the entire style string
5. Use it in the `style` parameter when adding shapes

### Common Custom Shapes

Here are some commonly used custom shape styles:

- **Person/Actor**: `shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;`
- **Document**: `shape=document;whiteSpace=wrap;html=1;`
- **Database (alternate)**: `shape=datastore;whiteSpace=wrap;html=1;`
- **Process**: `shape=process;whiteSpace=wrap;html=1;backgroundOutline=1;`
- **Manual Input**: `shape=manualInput;whiteSpace=wrap;html=1;`
- **Delay**: `shape=delay;whiteSpace=wrap;html=1;`
- **Display**: `shape=display;whiteSpace=wrap;html=1;`
- **Note**: `shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;`
- **Card**: `shape=card;whiteSpace=wrap;html=1;`
- **Tape**: `shape=tape;whiteSpace=wrap;html=1;`

This gives you access to **hundreds of shapes** including:
- UML diagrams (classes, actors, use cases)
- Network diagrams (Cisco, AWS, Azure icons)
- Flowchart symbols
- Entity-relationship symbols
- And many more!

### Styling Tips

You can also customize colors, borders, and fonts:

```
Create a shape with custom styling:
- Label: "Important Process"
- Style: "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1"
```

This creates a blue rounded rectangle with bold text.

## Connection Label Positioning

### Example 7: Customizing Connection Label Positions

**Prompt to AI:**
```
Create a workflow diagram with customized connection labels:
- Create three nodes: "Start", "Process", and "End"
- Connect Start to Process with a center-aligned label "Initialize"
- Connect Process to End with a label "Complete" offset 20 pixels right and 10 pixels down
- Add a self-loop from Process to Process with a label that has a yellow background
```

**Expected Result:**
A diagram with three nodes and connections that have customized label positions.

### Connection Label Features

The MCP server now supports fine-grained control over connection label positioning:

1. **Label Position** - Align label relative to the edge:
   ```
   Add connection with label_position="left" (or "right", "center")
   ```

2. **Label Offset** - Precise pixel-level positioning:
   ```
   Add connection with label_offset_x=20, label_offset_y=-10
   ```

3. **Label Background Color** - Highlight labels with background:
   ```
   Add connection with label_background_color="#ffeb3b"
   ```

4. **Combine Features** - Use all features together:
   ```
   Add connection with:
   - label_position="right"
   - label_offset_x=-5
   - label_offset_y=10
   - label_background_color="#e3f2fd"
   ```

This gives you complete control over how connection labels appear in your diagrams!

## Activity Diagrams

### Example 8: Creating an Activity Diagram

**Prompt to AI:**
```
Create an activity diagram for a user login process:
- Start node (activity_start)
- "Enter Credentials" action (activity_action)
- "Valid?" decision (activity_decision)
- Fork node for parallel tasks (activity_fork)
- "Log Activity" action (activity_action)
- "Load Profile" action (activity_action)
- Join node (activity_join)
- End node (activity_end)
- Add a note (activity_note) explaining the validation process
```

**Expected Result:**
A complete activity diagram with start/end nodes, actions, decision points, and parallel execution paths.

### Activity Diagram Shape Types

The MCP server now supports specialized shapes for UML activity diagrams:

- **`activity_start`** - Start node (filled black circle)
- **`activity_end`** - End node (filled circle with thick border)
- **`activity_action`** - Action/activity (rounded rectangle)
- **`activity_decision`** - Decision node (diamond)
- **`activity_fork`** - Fork node (thick horizontal/vertical bar for splitting parallel flows)
- **`activity_join`** - Join node (thick horizontal/vertical bar for merging parallel flows)
- **`activity_send_signal`** - Send signal shape
- **`activity_receive_signal`** - Receive signal shape
- **`activity_note`** - Note/comment annotation

### Example 9: Advanced Activity Diagram with Parallel Flows

**Prompt to AI:**
```
Create an activity diagram for order processing with parallel execution:
1. Start with activity_start
2. "Receive Order" (activity_action)
3. "Validate Order" (activity_decision)
4. If valid, use activity_fork to split into parallel tasks:
   - "Process Payment" (activity_action)
   - "Reserve Inventory" (activity_action)
5. Use activity_join to merge the parallel flows
6. "Ship Order" (activity_action)
7. End with activity_end

Add a note (activity_note) explaining that payment and inventory are processed in parallel.
```

## Swimlane Diagrams

### Example 10: Creating a Swimlane Diagram

**Prompt to AI:**
```
Create a horizontal swimlane diagram for a customer support process:
- Create a pool "Customer Support Process" (swimlane_pool)
- Add three horizontal lanes (swimlane_h):
  - "Customer" lane
  - "Support Agent" lane
  - "Technical Team" lane
- Add activities in each lane:
  - Customer: "Submit Ticket" (activity_action)
  - Support Agent: "Review Ticket" (activity_action), "Assign to Tech" (activity_action)
  - Technical Team: "Investigate" (activity_action), "Resolve Issue" (activity_action)
- Connect the activities with arrows showing the flow
```

**Expected Result:**
A swimlane diagram with three horizontal lanes showing the cross-functional process flow.

### Swimlane Shape Types

The MCP server supports swimlane diagrams for showing cross-functional processes:

- **`swimlane_pool`** - Overall container/pool for the entire process
- **`swimlane_h`** - Horizontal swimlane (lane goes left-to-right)
- **`swimlane_v`** - Vertical swimlane (lane goes top-to-bottom)
- **`container`** - Generic container for grouping related elements

### Example 11: Vertical Swimlane Diagram

**Prompt to AI:**
```
Create a vertical swimlane diagram for a software development pipeline:
- Create a container "CI/CD Pipeline" (container)
- Add three vertical lanes (swimlane_v):
  - "Build" stage
  - "Test" stage
  - "Deploy" stage
- Add activities in each stage:
  - Build: "Compile Code" (activity_action)
  - Test: "Run Tests" (activity_action), "Security Scan" (activity_action)
  - Deploy: "Deploy to Staging" (activity_action), "Deploy to Production" (activity_action)
- Connect activities showing the pipeline flow
```

### Tips for Activity and Swimlane Diagrams

1. **Use the right shapes for the job**:
   - Activity diagrams: Use activity_start/end for clear flow boundaries
   - Use activity_fork/join for parallel execution
   - Use activity_decision for branching logic

2. **Swimlane organization**:
   - Use swimlane_h for processes that flow left-to-right (horizontal)
   - Use swimlane_v for processes that flow top-to-bottom (vertical)
   - Place activities within their appropriate lane to show responsibility

3. **Combine with other shapes**:
   - You can mix activity shapes with basic shapes for flexibility
   - Use activity_note to add explanatory comments
   - Use connections with labels to show transitions and conditions

## UML Class Diagrams

### Example 12: Creating a UML Class Diagram

**Prompt to AI:**
```
Create a UML class diagram for a simple e-commerce system:
- Create a User class (uml_class) with attributes: id, email, password
- Create a Customer class (uml_class) extending User with attribute: address
- Create a Product class (uml_class) with attributes: id, name, price
- Create an Order class (uml_class) with attributes: id, date, total
- Create a PaymentProcessor interface (uml_interface) with method: processPayment()
- Connect Customer to User with inheritance (solid line, hollow arrow)
- Connect Customer to Order with association (solid line, open arrow)
- Connect Order to Product with association
- Connect Order to PaymentProcessor with dependency (dashed line, open arrow)
```

**Expected Result:**
A UML class diagram showing classes, interfaces, inheritance, associations, and dependencies.

### UML Class Diagram Shape Types

The MCP server supports specialized shapes for UML class diagrams:

- **`uml_class`** - Standard UML class with compartments for attributes and methods
- **`uml_interface`** - Interface (displayed with italic font style)
- **`uml_abstract_class`** - Abstract class (displayed with italic font style)
- **`uml_enum`** - Enumeration type
- **`uml_package`** - Package/namespace container
- **`uml_note`** - UML note/comment annotation

### UML Relationship Styles

Use these style strings for different UML relationships:

- **Inheritance (Generalization)**: `style="endArrow=block;endFill=0;endSize=12;"`
  - Solid line with hollow triangle arrow
  
- **Interface Implementation (Realization)**: `style="endArrow=block;dashed=1;endFill=0;endSize=12;"`
  - Dashed line with hollow triangle arrow
  
- **Association**: `style="endArrow=open;endSize=12;"`
  - Solid line with open arrow
  
- **Dependency**: `style="endArrow=open;dashed=1;endSize=12;"`
  - Dashed line with open arrow
  
- **Composition**: `style="endArrow=diamondThin;endFill=1;endSize=12;"`
  - Solid line with filled diamond
  
- **Aggregation**: `style="endArrow=diamondThin;endFill=0;endSize=12;"`
  - Solid line with hollow diamond

### Example 13: Comprehensive Library System UML Diagram

**Prompt to AI:**
```
Create a comprehensive UML class diagram for a library management system:
- Create a uml_package named "library.management"
- Inside the package, create these classes:
  - Book (uml_class) with attributes: isbn, title, author, year
  - Member (uml_class) with attributes: id, name, email
  - Loan (uml_class) with attributes: id, loanDate, returnDate
  - User (uml_abstract_class) with attributes: username, password
  - Librarian (uml_class) with attribute: employeeId
  - Searchable (uml_interface) with methods: search(), filter()
  - BookStatus (uml_enum) with values: AVAILABLE, LOANED, REPAIR, LOST
- Add relationships:
  - Loan has Book (association)
  - Loan has Member (association)
  - Member extends User (inheritance)
  - Librarian extends User (inheritance)
  - Book implements Searchable (realization)
  - Book uses BookStatus (dependency)
- Add a uml_note explaining the system
```

**Expected Result:**
A comprehensive UML class diagram with package, classes, abstract class, interface, enum, and various relationships.

### Example 14: Simple Inheritance Hierarchy

**Prompt to AI:**
```
Create a simple animal hierarchy UML class diagram:
- Create an Animal abstract class (uml_abstract_class) with attributes: name, age
- Create Dog, Cat, and Bird classes (uml_class) extending Animal
- Create a Pet interface (uml_interface) with methods: play(), feed()
- Connect Dog and Cat to Pet interface with realization
- Add specific attributes to each animal (breed for Dog, indoor for Cat, canFly for Bird)
```

### Tips for UML Class Diagrams

1. **Class structure formatting**:
   - Separate class name, attributes, and methods with horizontal lines (use `───────`)
   - Use visibility markers: `+` for public, `-` for private, `#` for protected
   - Format: `ClassName\n───────\n- attribute: Type\n───────\n+ method(): ReturnType`

2. **Stereotypes and markers**:
   - Use `«interface»` for interfaces
   - Use `«enumeration»` for enums
   - Use `«abstract»` or italic style for abstract classes

3. **Choose the right relationship type**:
   - **Inheritance**: "is-a" relationship (Dog is an Animal)
   - **Realization**: Implementing an interface (Class implements Interface)
   - **Association**: "has-a" or "uses-a" relationship (Order has Products)
   - **Dependency**: One class depends on another temporarily (Order uses PaymentProcessor)
   - **Composition**: Strong ownership (Car has Engine - engine cannot exist without car)
   - **Aggregation**: Weak ownership (Department has Employees - employees can exist independently)

4. **Package organization**:
   - Use `uml_package` to group related classes
   - Place the package shape first, then add classes inside its bounds

See `UML_CLASS_DIAGRAM_EXAMPLES.md` for detailed code examples and more advanced usage patterns.
