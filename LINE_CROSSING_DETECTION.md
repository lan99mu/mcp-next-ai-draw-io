# Line Crossing Detection Feature

## Overview

This document describes the line crossing detection feature added to the MCP Draw.io Server. This feature automatically detects when connections (lines/edges) cross each other in diagrams and provides actionable position hints to help AI models adjust the layout.

## Problem Statement

In Chinese: "我觉得mcp服务应该对于连线交叉的给出位置提示，供大模型调整"

Translation: "I think the MCP service should provide position hints for line crossings, for the large model to adjust"

## Solution

### Architecture

The solution consists of three main components:

1. **crossing_detector.py** - A new utility module containing:
   - `get_connection_endpoints()` - Calculates effective start/end points of connections
   - `line_segments_intersect()` - Detects if two line segments intersect
   - `detect_crossings()` - Main function that detects all crossings in a diagram
   - `_generate_crossing_suggestion()` - Generates helpful suggestions for fixing crossings

2. **Server Integration** - Added a new MCP tool `detect_line_crossings`:
   - Works with both programmatically created diagrams and loaded .drawio files
   - Returns detailed crossing information in a human-readable format
   - Provides multiple suggestions for each crossing

3. **Documentation** - Updated both English and Chinese README files with:
   - Feature description in the core capabilities list
   - Tool reference entry
   - Detailed usage examples and benefits

### How It Works

1. **Input**: The tool analyzes the current diagram (either from `current_xml` or `current_diagram`)

2. **Processing**:
   - Separates shapes and connections from all cells
   - For each pair of connections:
     - Calculates effective endpoints (considering entry/exit points)
     - Checks if the line segments intersect
     - If they do, records the intersection point and generates suggestions

3. **Output**: Returns a formatted report containing:
   - Total number of crossings detected
   - For each crossing:
     - IDs and labels of the crossing connections
     - Exact intersection point coordinates (x, y)
     - Multiple actionable suggestions:
       1. Add waypoints to route connections around each other
       2. Reposition shapes to avoid crossings
       3. Adjust entry/exit points to change connection angles

## Usage Example

```python
# Via MCP tool
detect_line_crossings()

# Example output:
"""
Detected 2 line crossing(s):

1. Crossing between:
   - Connection 'Read Cache' (ID: conn_5)
   - Connection 'Query DB' (ID: conn_6)
   Lines cross at (260.0, 180.0). Consider these adjustments:
     1. Add waypoints to 'Read Cache' to route around the crossing
     2. Add waypoints to 'Query DB' to route around the crossing
     3. Reposition shapes connected by 'Read Cache' to avoid crossing
     4. Reposition shapes connected by 'Query DB' to avoid crossing
     5. Adjust entry/exit points to change connection angles
"""
```

## Benefits

1. **Automatic Detection**: AI models can automatically identify layout problems
2. **Precise Information**: Provides exact coordinates of each crossing
3. **Actionable Suggestions**: Offers multiple specific ways to fix each issue
4. **Improved Readability**: Helps create cleaner, more professional diagrams
5. **AI-Friendly**: Designed to help AI models make better layout decisions

## Implementation Details

### Line Intersection Algorithm

Uses the parametric line equation method:
- Given two line segments (p1-p2) and (p3-p4)
- Calculates parameters t and u where the lines would intersect
- If both 0 ≤ t ≤ 1 and 0 ≤ u ≤ 1, the segments intersect
- Returns the exact intersection point coordinates

### Connection Endpoint Calculation

Handles multiple cases:
- Explicit source/target points if specified
- Entry/exit points (normalized 0-1 coordinates on shape boundaries)
- Default to shape center if no specific points are given

### Future Enhancements

The current implementation detects crossings for simple direct connections. Future enhancements could include:

1. **Waypoint Support**: Check each segment between consecutive waypoints for intersections
   - Get waypoint list from connection
   - Create segments: start→wp1, wp1→wp2, ..., wpN→end
   - Check each segment pair for intersections

2. **Smart Suggestions**: Provide more specific waypoint coordinates based on the crossing location

3. **Auto-Fix**: Automatically add waypoints or adjust entry/exit points to eliminate crossings

## Testing

Comprehensive tests were added in `test_crossing_detection.py`:

1. **Basic Crossing Detection**: Verifies detection of simple diagonal line crossings
2. **No Crossing Detection**: Ensures parallel/separate lines aren't flagged
3. **Multiple Crossings**: Tests complex diagrams with many connections

All tests pass successfully, confirming the feature works as expected.

## Security

CodeQL analysis was run on the new code - **no security alerts** were found.

## Code Review

Code review feedback was addressed:
- Removed unused variables (mid_x, mid_y)
- Improved TODO comment with detailed implementation notes

## Files Modified/Added

### New Files:
- `mcp_drawio_server/crossing_detector.py` - Core crossing detection logic
- `test_crossing_detection.py` - Comprehensive test suite
- `demo_crossing_detection.py` - Demo script showing the feature in action
- `LINE_CROSSING_DETECTION.md` - This documentation file

### Modified Files:
- `mcp_drawio_server/server.py` - Added new MCP tool and handler
- `README.md` - Added feature documentation (English)
- `README_CN.md` - Added feature documentation (Chinese)

## Conclusion

This feature successfully addresses the original problem statement by providing the MCP service with the ability to detect line crossings and offer position hints for AI models to adjust diagram layouts. The implementation is clean, well-tested, secure, and fully documented in both English and Chinese.
