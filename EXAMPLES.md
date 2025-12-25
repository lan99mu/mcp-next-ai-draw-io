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

You can specify custom Draw.io styles:

```
Create a shape with custom style:
- Label: "Important Process"
- Style: "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1"
```

This creates a blue rounded rectangle with bold text.
