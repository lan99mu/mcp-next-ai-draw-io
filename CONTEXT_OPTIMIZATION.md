# Context Optimization Guide

## Overview

This MCP server has been optimized to reduce context consumption in VS Code Copilot by **62.2%** while still providing comprehensive documentation on-demand.

## The Problem

Previously, all tool descriptions were very verbose with embedded guidance like:
- "IMPORTANT: Check bindings before..."
- "BEST PRACTICE: Bind related nodes..."
- "USE THIS when nodes are..."

This consumed excessive tokens in the initial context when Copilot loaded the tools.

**Old total:** 2,669 characters in tool descriptions

## The Solution

We split information into two layers:

### Layer 1: Concise Tool Descriptions (Initial Context)
- Only essential "what it does" information
- Loaded immediately with tools
- Minimal token consumption

**New total:** 1,010 characters (62.2% reduction)

### Layer 2: Detailed Documentation (On-Demand)
- Comprehensive guides and examples
- Accessed only when needed via MCP Resources
- 15,546 characters of detailed docs

## How It Works

### For VS Code Copilot Users

**Initial Load (Automatic):**
```
VS Code Copilot loads server → Gets concise tool descriptions
Example: "bind_nodes: Bind multiple nodes to move together as a group."
```

**On-Demand Details (When Needed):**
```
User/Agent requests: "Show me detailed binding documentation"
Copilot calls: resources/read with uri="docs://bindings/guide"
Returns: 3,651 chars of comprehensive binding guide
```

### Available Resources

1. **docs://tools/overview**
   - Complete tool documentation
   - Parameters and usage examples
   - Best practices for each tool
   - 4,961 characters

2. **docs://bindings/guide**
   - Complete node bindings guide
   - Efficiency patterns and examples
   - Common patterns and troubleshooting
   - 3,651 characters

3. **docs://workflows/best-practices**
   - Workflow efficiency principles
   - Common patterns and anti-patterns
   - Tool call reduction strategies
   - 3,710 characters

4. **docs://shapes/reference**
   - All available shape types
   - Usage examples for each type
   - Recommended dimensions
   - 3,224 characters

## Accessing Resources

### Via MCP Protocol

**List available resources:**
```json
{
  "method": "resources/list"
}
```

**Read a specific resource:**
```json
{
  "method": "resources/read",
  "params": {
    "uri": "docs://bindings/guide"
  }
}
```

### Via VS Code Copilot Chat

Users can ask:
- "Show me the bindings guide"
- "What are the available shape types?"
- "How do I use node bindings efficiently?"

Copilot will automatically fetch the relevant resource.

## Benefits

### For Token Efficiency

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Initial context | 2,669 chars | 1,010 chars | 62.2% |
| Per-tool average | 148 chars | 56 chars | 62.2% |
| Detailed docs | In context | On-demand | 0 → 15,546 chars when needed |

### For User Experience

✅ **Faster loading** - Less initial context to process
✅ **Lower costs** - Fewer tokens in every request
✅ **Better focus** - Concise descriptions, details when needed
✅ **Comprehensive docs** - More detailed than before, just on-demand

## Implementation Details

### Concise Descriptions

**Before:**
```python
Tool(
    name="bind_nodes",
    description="Bind multiple nodes together so they move as a group. When you move one node in a bound group, all bound nodes will move together by the same offset. USE THIS when nodes are logically related (e.g., a service and its database, a component and its label). This enables EFFICIENT LOCAL ADJUSTMENTS - you only need to move ONE node instead of multiple nodes individually. BEST PRACTICE: Bind related nodes immediately after creating them."
)
# 435 characters
```

**After:**
```python
Tool(
    name="bind_nodes",
    description="Bind multiple nodes to move together as a group."
)
# 48 characters (89% reduction)
```

Detailed information moved to `docs://bindings/guide` resource.

### Resource Structure

Resources are organized by topic:
- **tools/** - Tool-specific documentation
- **bindings/** - Node binding guides
- **workflows/** - Workflow patterns
- **shapes/** - Shape type references

All use `docs://` URI scheme for clarity.

## Migration Notes

### For Existing Users

No breaking changes! All tools work exactly the same.

**What changed:**
- Tool descriptions are now concise
- Detailed docs moved to resources

**What to do:**
- Nothing required
- Optionally, start using resources for detailed info

### For New Integrations

**Recommended pattern:**
1. Use concise tool descriptions for initial understanding
2. Access resources when detailed info is needed
3. Leverage prompts for workflow guidance

## Comparison with Prompts

Both features reduce context consumption:

| Feature | Purpose | When to Use |
|---------|---------|-------------|
| **Concise Descriptions** | Essential tool info | Always (automatic) |
| **Resources** | Detailed documentation | When details needed |
| **Prompts** | Workflow templates | When following patterns |

**Workflow:**
1. Tools loaded with concise descriptions (minimal context)
2. Prompts guide workflows (on-demand)
3. Resources provide details (on-demand)

## Examples

### Example 1: Quick Tool Use

```
User: "List all cells in my diagram"
Copilot sees: "list_cells: List all cells with IDs, labels, types, and bindings."
Copilot calls: list_cells()
Result: ✓ Done, 56 chars consumed
```

### Example 2: Need Detailed Info

```
User: "How do bindings work? I need details."
Copilot accesses: docs://bindings/guide (3,651 chars)
Copilot explains: [Detailed binding explanation]
Result: ✓ Done, detailed info provided when needed
```

### Example 3: Following a Workflow

```
User: "Create a flowchart efficiently"
Copilot uses: Prompt "create_flowchart"
Copilot may also access: docs://workflows/best-practices
Result: ✓ Guided workflow with details as needed
```

## Metrics

### Context Savings

For a typical workflow session:

**Before:**
- Initial load: 2,669 chars (tool descriptions)
- Every request includes full descriptions

**After:**
- Initial load: 1,010 chars (concise descriptions)
- Details only when requested

**Savings per session:**
- Minimum: 1,659 chars (62.2%)
- Typical: 1,659+ chars (since most sessions don't need all details)

### Cost Impact

Assuming:
- 1 token ≈ 4 characters
- Tool descriptions sent in every request

**Before:** ~667 tokens per request
**After:** ~253 tokens per request
**Savings:** ~414 tokens per request (62%)

Over 100 requests: **~41,400 tokens saved**

## Future Enhancements

Potential future resources:
- `docs://examples/flowcharts` - Flowchart examples
- `docs://examples/architecture` - Architecture diagram examples
- `docs://troubleshooting/common-issues` - Common problems and solutions
- `docs://api/xml-format` - Draw.io XML format reference

## Summary

**Key Achievement:**
✅ 62.2% reduction in initial context consumption
✅ More detailed documentation than before
✅ Available on-demand when needed
✅ Zero breaking changes

This directly addresses: "减少描述在上下文中的消耗，让copilot按需获取明细描述" (Reduce description consumption in context, allow Copilot to get detailed descriptions on-demand)
