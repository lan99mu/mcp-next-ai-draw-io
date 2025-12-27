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
