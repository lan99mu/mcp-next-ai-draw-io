#!/usr/bin/env python3
"""
MCP Prompts for Draw.io Server.

This module contains prompt definitions and handlers for workflow templates.
"""

from mcp.types import (
    Prompt, PromptArgument, PromptMessage, GetPromptResult, TextContent
)


def get_prompt_definitions() -> list[Prompt]:
    """Return all available prompt template definitions."""
    return [
        Prompt(
            name="create_flowchart",
            description="Efficiently create a flowchart diagram with proper node placement and automatic bindings for related elements. This workflow guides you through creating nodes, connecting them, and using bindings to group related elements.",
            arguments=[
                PromptArgument(
                    name="description",
                    description="High-level description of the flowchart (e.g., 'user login process', 'order fulfillment workflow')",
                    required=True
                )
            ]
        ),
        Prompt(
            name="add_connected_nodes",
            description="Add multiple related nodes with connections and automatic bindings. Best for extending existing diagrams efficiently by creating a group of related nodes that can be moved together.",
            arguments=[
                PromptArgument(
                    name="nodes_description",
                    description="Description of the nodes to add and their relationships (e.g., 'service, database, and cache nodes connected in sequence')",
                    required=True
                ),
                PromptArgument(
                    name="base_x",
                    description="Starting X coordinate for the new nodes (optional, default: 0)",
                    required=False
                ),
                PromptArgument(
                    name="base_y", 
                    description="Starting Y coordinate for the new nodes (optional, default: 0)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="optimize_layout",
            description="Optimize diagram layout by detecting and fixing line crossings, suggesting bindings, and improving spacing. This helps clean up messy diagrams with minimal manual adjustments.",
            arguments=[]
        ),
        Prompt(
            name="modify_with_bindings",
            description="Efficiently modify an existing diagram by leveraging node bindings. This workflow shows how to check existing bindings and use them to make local adjustments by moving just one node instead of many.",
            arguments=[
                PromptArgument(
                    name="modification_description",
                    description="Description of what to modify (e.g., 'move the authentication section down', 'adjust database cluster spacing')",
                    required=True
                )
            ]
        ),
        Prompt(
            name="create_architecture_diagram",
            description="Create a software architecture diagram with proper layering and component grouping. Uses bindings to group related components that should move together.",
            arguments=[
                PromptArgument(
                    name="architecture_description",
                    description="Description of the architecture (e.g., '3-tier web application', 'microservices with API gateway')",
                    required=True
                )
            ]
        )
    ]


def get_prompt_result(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific prompt template with instructions."""
    
    if name == "create_flowchart":
        description = arguments.get("description", "a flowchart") if arguments else "a flowchart"
        
        return GetPromptResult(
            description=f"Create {description} efficiently using bindings",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Create a flowchart for: {description}

WORKFLOW (follow this order to minimize model calls):

1. **Plan the structure**: Think about the main steps and their relationships
2. **Create nodes in logical groups**: 
   - Use add_shape() to create related nodes (e.g., all decision nodes, all process nodes)
   - Place them with proper spacing (150-200px between nodes)
3. **Bind related nodes immediately**:
   - After creating a group of related nodes, use bind_nodes() to group them
   - Example: bind_nodes(node_ids=["start", "process1", "decision1"])
   - This allows you to move the entire group by adjusting just ONE node later
4. **Add connections**: 
   - Use add_connection() between nodes
   - Set proper entry/exit points for clean routing
5. **Use suggest_bindings()**: 
   - Check for additional binding opportunities
   - Bind nodes that should move together
6. **Check for crossings**:
   - Use detect_line_crossings() to identify issues
   - Fix by moving just ONE node from bound groups (all bound nodes move automatically)

BEST PRACTICES:
✓ Bind nodes EARLY (right after creation)
✓ Use vertical spacing of 150-200px between levels
✓ Use horizontal spacing of 200-250px between parallel paths
✓ Move bound groups by adjusting just ONE node, not all nodes individually
✓ Check suggest_bindings() after creating the initial structure

This approach reduces model calls by 60-80% compared to adjusting each node individually!"""
                    )
                )
            ]
        )
    
    elif name == "add_connected_nodes":
        nodes_desc = arguments.get("nodes_description", "related nodes") if arguments else "related nodes"
        base_x = arguments.get("base_x", "0") if arguments else "0"
        base_y = arguments.get("base_y", "0") if arguments else "0"
        
        return GetPromptResult(
            description=f"Add {nodes_desc} with automatic bindings",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Add {nodes_desc} to the diagram starting at position ({base_x}, {base_y})

EFFICIENT WORKFLOW:

1. **List existing cells** to understand the current diagram:
   - Use list_cells() to see what already exists
   - Note any existing bindings (shown as [BOUND to: ...])
   
2. **Create all new nodes in one batch**:
   - Use add_shape() for each node with proper spacing
   - Keep track of the created node IDs
   
3. **Bind the new nodes together IMMEDIATELY**:
   - Use bind_nodes(node_ids=[id1, id2, id3, ...])
   - This creates a movable group
   
4. **Add connections**:
   - Connect the nodes using add_connection()
   - Connect to existing nodes if needed
   
5. **Verify and optimize**:
   - Use suggest_bindings() to check if these new nodes should be bound to existing nodes
   - If the new nodes should move with existing groups, add those bindings too

EXAMPLE:
```
# Create nodes
svc_id = add_shape(label="Service", x=100, y=100)
db_id = add_shape(label="Database", x=100, y=200) 
cache_id = add_shape(label="Cache", x=250, y=200)

# Bind immediately - this is KEY for efficiency!
bind_nodes(node_ids=[svc_id, db_id, cache_id])

# Add connections
add_connection(source_id=svc_id, target_id=db_id)
add_connection(source_id=svc_id, target_id=cache_id)

# Now moving any ONE of these nodes moves all 3 together!
```

This saves 2-3 tool calls per adjustment compared to moving nodes individually."""
                    )
                )
            ]
        )
    
    elif name == "optimize_layout":
        return GetPromptResult(
            description="Optimize diagram layout with minimal adjustments",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Optimize the current diagram layout efficiently

OPTIMIZATION WORKFLOW:

1. **Detect crossings**:
   - Use detect_line_crossings() to find all crossing issues
   - This identifies which nodes need adjustment
   
2. **Suggest bindings** before making changes:
   - Use suggest_bindings() to identify nodes that should move together
   - Bind related nodes BEFORE adjusting positions
   - This ensures when you move one node, related nodes move too
   
3. **Apply bindings strategically**:
   - For each high-scoring suggestion, use bind_nodes()
   - Focus on binding nodes that are:
     * Close together (proximity)
     * Have matching names (same prefix/suffix)
     * Are functionally related (service+db, ui+api, etc.)
   
4. **Fix crossings with minimal moves**:
   - For each crossing, move just ONE node from the bound group
   - All bound nodes will move automatically
   - Verify crossings are resolved with detect_line_crossings()
   
5. **Final spacing check**:
   - Use suggest_bindings() again to see if any new opportunities emerged
   - Verify layout looks clean with list_cells()

EFFICIENCY GAIN:
- Without bindings: Need to move each node individually = 5-10 tool calls per section
- With bindings: Move one node per bound group = 1-2 tool calls per section
- Result: 70-80% reduction in tool calls

IMPORTANT: Always bind BEFORE moving nodes to maximize efficiency!"""
                    )
                )
            ]
        )
    
    elif name == "modify_with_bindings":
        modification = arguments.get("modification_description", "the diagram") if arguments else "the diagram"
        
        return GetPromptResult(
            description=f"Modify {modification} using efficient binding-based workflow",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Modify the diagram: {modification}

BINDING-AWARE MODIFICATION WORKFLOW:

1. **Check existing bindings FIRST**:
   - Use list_cells() to see all nodes and their bindings
   - Look for [BOUND to: ...] annotations
   - This tells you which nodes already move together
   
2. **Identify the modification scope**:
   - Which nodes need to move?
   - Are they already bound together?
   - If not, should they be bound?
   
3. **Create new bindings if needed**:
   - If multiple unbound nodes need to move together, bind them first
   - Use bind_nodes(node_ids=[...])
   - This is a one-time setup that saves many future calls
   
4. **Make the modification efficiently**:
   - Move just ONE node from each bound group
   - Use move_shape(shape_id=one_node_id, new_x=..., new_y=...)
   - All bound nodes move automatically
   
5. **Verify the change**:
   - Use list_cells() to confirm positions
   - Use detect_line_crossings() to check for new issues

EXAMPLE - Moving a service cluster:
```
# Without bindings (inefficient):
move_shape("svc1", 300, 100)  # Call 1
move_shape("svc2", 300, 200)  # Call 2  
move_shape("db1", 300, 300)   # Call 3
move_shape("cache1", 450, 300) # Call 4
# Total: 4 calls

# With bindings (efficient):
bind_nodes(["svc1", "svc2", "db1", "cache1"])  # One-time setup
move_shape("svc1", 300, 100)  # Just ONE call - all 4 move!
# Total: 2 calls (and future modifications only need 1 call)
```

KEY INSIGHT: Bindings are an INVESTMENT - spend 1 call to set them up, save 3-10 calls on every future adjustment!"""
                    )
                )
            ]
        )
    
    elif name == "create_architecture_diagram":
        arch_desc = arguments.get("architecture_description", "a system architecture") if arguments else "a system architecture"
        
        return GetPromptResult(
            description=f"Create {arch_desc} with proper component grouping",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Create an architecture diagram for: {arch_desc}

ARCHITECTURE DIAGRAM WORKFLOW:

1. **Plan layers/tiers**:
   - Identify logical layers (e.g., presentation, business, data)
   - Plan vertical spacing: 250-300px between layers
   - Plan horizontal spacing: 200-250px between components
   
2. **Create components layer by layer**:
   - Start with the top layer (e.g., UI/frontend)
   - Use add_shape() for each component
   - Use consistent Y coordinates within a layer
   
3. **Bind components within each layer**:
   - After creating all components in a layer, bind them
   - Example: bind_nodes(["ui1", "ui2", "ui3"])
   - This allows moving entire layers together
   
4. **Create cross-layer component groups**:
   - For vertical stacks (e.g., service + its database), bind them too
   - Use suggest_bindings() to identify these relationships
   - Bind vertical stacks: bind_nodes(["service", "service_db", "service_cache"])
   
5. **Add connections**:
   - Connect components with add_connection()
   - Use entry/exit points for clean routing
   - Add waypoints if needed for complex routing
   
6. **Optimize layout**:
   - Use detect_line_crossings() to find issues
   - Move one node per bound group to fix crossings
   - All bound components move together

LAYERING STRATEGY:
```
Layer 1 (Y=100): UI components - bind together
Layer 2 (Y=350): API/Service components - bind together  
Layer 3 (Y=600): Data components - bind together

Vertical stacks: Each service+db+cache stack bound together

Result:
- Move entire layers by adjusting ONE node
- Move service stacks by adjusting ONE component
- Total tool calls reduced by 75-85%
```

BEST PRACTICES:
✓ Bind horizontally (all components in a layer)
✓ Bind vertically (component + its dependencies)
✓ Use suggest_bindings() to discover implicit relationships
✓ Test moving one node per group to verify bindings work"""
                    )
                )
            ]
        )
    
    else:
        return GetPromptResult(
            description=f"Unknown prompt: {name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Prompt '{name}' not found. Use list_prompts to see available prompts."
                    )
                )
            ]
        )
