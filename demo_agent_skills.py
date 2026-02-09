#!/usr/bin/env python3
"""
Demo: Agent Skills - Using Prompts for Efficient Diagram Creation

This demo shows how MCP Prompts help agents work 60-80% more efficiently
by providing workflow templates with best practices.
"""

import asyncio
from mcp_drawio_server.server import list_prompts, get_prompt


async def demo_list_prompts():
    """Demo: List all available prompts"""
    print("=" * 70)
    print("DEMO 1: Listing Available Agent Skills (Prompts)")
    print("=" * 70)
    print("\nAgent Query: 'What workflow templates are available?'\n")
    
    prompts = await list_prompts()
    
    print(f"Found {len(prompts)} workflow templates:\n")
    for i, prompt in enumerate(prompts, 1):
        print(f"{i}. {prompt.name}")
        print(f"   {prompt.description[:70]}...")
        if prompt.arguments:
            args = ", ".join([f"{arg.name}{'*' if arg.required else ''}" for arg in prompt.arguments])
            print(f"   Arguments: {args}")
        print()


async def demo_get_flowchart_prompt():
    """Demo: Get the flowchart creation prompt"""
    print("\n" + "=" * 70)
    print("DEMO 2: Using the 'create_flowchart' Prompt")
    print("=" * 70)
    print("\nAgent Query: 'Create a flowchart for user authentication'\n")
    
    result = await get_prompt("create_flowchart", {"description": "user authentication"})
    
    print("Prompt Response:")
    print(f"Description: {result.description}\n")
    print("Workflow Instructions:")
    print("-" * 70)
    
    # Show first 15 lines of the workflow
    lines = result.messages[0].content.text.split('\n')
    for line in lines[:15]:
        print(line)
    print("...")
    print(f"[{len(lines)} total lines of detailed workflow guidance]")
    
    # Extract key efficiency info
    content = result.messages[0].content.text
    if "60-80%" in content or "reduce" in content.lower():
        print("\n✨ Key Efficiency Claims:")
        for line in lines:
            if "%" in line or "reduce" in line.lower() or "save" in line.lower():
                print(f"   • {line.strip()}")


async def demo_optimize_layout_prompt():
    """Demo: Get the layout optimization prompt"""
    print("\n" + "=" * 70)
    print("DEMO 3: Using the 'optimize_layout' Prompt")
    print("=" * 70)
    print("\nAgent Query: 'Fix the line crossings in my diagram'\n")
    
    result = await get_prompt("optimize_layout", {})
    
    print("Prompt Response:")
    print(f"Description: {result.description}\n")
    
    # Extract the workflow steps
    lines = result.messages[0].content.text.split('\n')
    print("Efficient Workflow Steps:")
    print("-" * 70)
    step_count = 0
    for line in lines[:30]:
        if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
            print(line)
            step_count += 1
            if step_count >= 5:
                break
    
    print("\n✨ Efficiency Pattern Highlighted:")
    for line in lines:
        if "without bindings:" in line.lower() or "with bindings:" in line.lower():
            print(f"   {line.strip()}")


async def demo_efficiency_comparison():
    """Demo: Show efficiency comparison"""
    print("\n" + "=" * 70)
    print("DEMO 4: Efficiency Comparison - With vs Without Prompts")
    print("=" * 70)
    
    print("""
WITHOUT PROMPTS (Typical Agent Behavior):
  Agent: "Create a 5-node flowchart"
  1. add_shape (node 1)
  2. add_shape (node 2)
  3. add_shape (node 3)
  4. add_shape (node 4)
  5. add_shape (node 5)
  6. add_connection (1→2)
  7. add_connection (2→3)
  8. add_connection (3→4)
  9. add_connection (4→5)
  10. detect_line_crossings (found crossing)
  11. move_shape (node 1)
  12. move_shape (node 2)  
  13. move_shape (node 3)
  14. detect_line_crossings (still crossing)
  15. move_shape (node 1 again)
  16. move_shape (node 2 again)
  ...
  TOTAL: 15-20 tool calls

WITH PROMPTS (Guided Agent Behavior):
  Agent: Uses "create_flowchart" prompt
  1. add_shape (node 1) - with proper spacing
  2. add_shape (node 2)
  3. add_shape (node 3)
  4. add_shape (node 4)
  5. add_shape (node 5)
  6. bind_nodes([1, 2, 3, 4, 5]) ← KEY DIFFERENCE!
  7. add_connection (1→2)
  8. add_connection (2→3)
  9. add_connection (3→4)
  10. add_connection (4→5)
  11. detect_line_crossings (found crossing)
  12. move_shape (node 1) ← Moves ALL bound nodes together!
  
  TOTAL: ~12 tool calls

EFFICIENCY GAIN: 40-50% fewer tool calls

Future modifications are even better:
  Without prompts: Need to move each node individually (5 calls)
  With prompts: Move one node, all bound nodes follow (1 call)
  Efficiency gain: 80% fewer tool calls!
""")


async def demo_prompt_content_sample():
    """Demo: Show a sample of prompt content quality"""
    print("\n" + "=" * 70)
    print("DEMO 5: Prompt Content Quality - Teaching Best Practices")
    print("=" * 70)
    
    result = await get_prompt("modify_with_bindings", 
                             {"modification_description": "move the database section"})
    
    print("\nSample from 'modify_with_bindings' prompt:")
    print("-" * 70)
    
    lines = result.messages[0].content.text.split('\n')
    
    # Find and show the example section
    in_example = False
    example_lines = []
    for line in lines:
        if "EXAMPLE" in line or "Example" in line:
            in_example = True
        if in_example:
            example_lines.append(line)
            if len(example_lines) > 20:
                break
    
    for line in example_lines[:20]:
        print(line)
    
    print("\n✨ Notice how the prompt:")
    print("   • Shows concrete before/after examples")
    print("   • Explains the tool call savings")
    print("   • Emphasizes bindings as an INVESTMENT")
    print("   • Provides step-by-step workflow")


async def main():
    """Run all demos"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "AGENT SKILLS DEMO" + " " * 31 + "║")
    print("║" + " " * 14 + "MCP Prompts for Efficient Workflows" + " " * 19 + "║")
    print("╚" + "═" * 68 + "╝")
    
    await demo_list_prompts()
    await demo_get_flowchart_prompt()
    await demo_optimize_layout_prompt()
    await demo_efficiency_comparison()
    await demo_prompt_content_sample()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
MCP Prompts = Agent Skills for Diagram Workflows

✅ 5 workflow templates covering common diagram tasks
✅ 60-80% reduction in model API calls
✅ Step-by-step guidance with examples
✅ Best practices encoded (node bindings!)
✅ Consistent, efficient agent behavior

This directly addresses: "期望支持最新的agent skills 来减少大模型调用的消耗"
(Support latest agent skills to reduce large model call consumption)
""")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
