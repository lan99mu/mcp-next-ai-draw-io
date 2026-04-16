#!/usr/bin/env python3
"""
Analysis operation handlers.

Handlers for detect_line_crossings and suggest_bindings tools.
"""

from typing import Any
from mcp.types import TextContent

from .state import diagram_state, safe_float
from ..xml_operations import get_cells_from_xml
from ..crossing_detector import detect_crossings
from ..overlap_detector import detect_overlaps


def handle_detect_line_crossings(arguments: Any) -> list[TextContent]:
    """Handle detect_line_crossings tool call."""
    if diagram_state.current_xml:
        cells = get_cells_from_xml(diagram_state.current_xml)
    elif diagram_state.current_diagram:
        xml_content = diagram_state.current_diagram.to_drawio_xml()
        cells = get_cells_from_xml(xml_content)
    else:
        return [TextContent(
            type="text",
            text="No diagram available. Create a new diagram or load an existing one."
        )]
    
    crossings = detect_crossings(cells)
    
    if not crossings:
        return [TextContent(
            type="text",
            text="No line crossings detected in the diagram. All connections are clear!"
        )]
    
    result_parts = [f"Detected {len(crossings)} line crossing(s):\n"]
    
    for i, crossing in enumerate(crossings, 1):
        result_parts.append(f"\n{i}. Crossing between:")
        result_parts.append(f"   - Connection '{crossing['connection1_label']}' (ID: {crossing['connection1_id']})")
        result_parts.append(f"   - Connection '{crossing['connection2_label']}' (ID: {crossing['connection2_id']})")
        result_parts.append(f"   {crossing['suggestion']}")
    
    return [TextContent(type="text", text="\n".join(result_parts))]


def handle_suggest_bindings(arguments: Any) -> list[TextContent]:
    """Handle suggest_bindings tool call."""
    if diagram_state.current_xml:
        cells = get_cells_from_xml(diagram_state.current_xml)
    elif diagram_state.current_diagram:
        xml_content = diagram_state.current_diagram.to_drawio_xml()
        cells = get_cells_from_xml(xml_content)
    else:
        return [TextContent(
            type="text",
            text="No diagram available. Create a new diagram or load an existing one."
        )]
    
    proximity_threshold = arguments.get("proximity_threshold", 200)
    
    shapes = [cell for cell in cells if cell.get('vertex')]
    
    if len(shapes) < 2:
        return [TextContent(
            type="text",
            text="Not enough shapes in the diagram to suggest bindings. Need at least 2 shapes."
        )]
    
    suggestions = []
    already_bound = set()
    
    for i, shape1 in enumerate(shapes):
        for shape2 in shapes[i + 1:]:
            shape1_id = shape1['id']
            shape2_id = shape2['id']
            
            bound_nodes_1 = shape1.get('bound_nodes', [])
            bound_nodes_2 = shape2.get('bound_nodes', [])
            if shape2_id in bound_nodes_1 or shape1_id in bound_nodes_2:
                pair_key = tuple(sorted([shape1_id, shape2_id]))
                already_bound.add(pair_key)
                continue
            
            x1 = safe_float(shape1.get('x', 0))
            y1 = safe_float(shape1.get('y', 0))
            w1 = safe_float(shape1.get('width', 120))
            h1 = safe_float(shape1.get('height', 60))
            center1_x = x1 + w1 / 2
            center1_y = y1 + h1 / 2
            
            x2 = safe_float(shape2.get('x', 0))
            y2 = safe_float(shape2.get('y', 0))
            w2 = safe_float(shape2.get('width', 120))
            h2 = safe_float(shape2.get('height', 60))
            center2_x = x2 + w2 / 2
            center2_y = y2 + h2 / 2
            
            distance = ((center2_x - center1_x) ** 2 + (center2_y - center1_y) ** 2) ** 0.5
            
            if distance <= proximity_threshold:
                label1 = shape1.get('value', shape1_id)
                label2 = shape2.get('value', shape2_id)
                
                reasons = []
                score = 0
                
                proximity_score = int((1 - distance / proximity_threshold) * 100)
                reasons.append(f"proximity: {proximity_score}% (distance: {distance:.1f}px)")
                score += proximity_score
                
                if abs(center1_x - center2_x) < 50:
                    reasons.append("vertically aligned")
                    score += 20
                
                if abs(center1_y - center2_y) < 50:
                    reasons.append("horizontally aligned")
                    score += 20
                
                label1_lower = label1.lower()
                label2_lower = label2.lower()
                
                label1_words = label1.split()
                label2_words = label2.split()
                if label1_words and label2_words:
                    if label1_words[-1] == label2_words[-1]:
                        reasons.append(f"naming pattern: same suffix '{label1_words[-1]}'")
                        score += 30
                    elif label1_words[0] == label2_words[0]:
                        reasons.append(f"naming pattern: same prefix '{label1_words[0]}'")
                        score += 25
                
                related_pairs = [
                    ('service', 'db'), ('service', 'database'),
                    ('api', 'db'), ('api', 'database'),
                    ('app', 'db'), ('app', 'database'),
                    ('frontend', 'backend'),
                    ('client', 'server'),
                    ('cache', 'db'), ('cache', 'database')
                ]
                
                for word1, word2 in related_pairs:
                    if (word1 in label1_lower and word2 in label2_lower) or \
                       (word2 in label1_lower and word1 in label2_lower):
                        reasons.append(f"related keywords: '{word1}' and '{word2}'")
                        score += 35
                        break
                
                if score >= 50:
                    suggestions.append({
                        'id1': shape1_id,
                        'id2': shape2_id,
                        'label1': label1,
                        'label2': label2,
                        'score': score,
                        'reasons': reasons,
                        'distance': distance
                    })
    
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    
    if not suggestions and not already_bound:
        return [TextContent(
            type="text",
            text=f"No binding suggestions found. No shapes are within {proximity_threshold}px of each other or have clear relationships."
        )]
    
    result_parts = []
    
    if already_bound:
        result_parts.append(f"✓ Found {len(already_bound)} existing binding(s):")
        for pair in sorted(already_bound):
            result_parts.append(f"  - {pair[0]} and {pair[1]} are already bound")
        result_parts.append("")
    
    if suggestions:
        result_parts.append(f"💡 Suggested {len(suggestions)} new binding(s) for efficient local adjustments:\n")
        
        for i, suggestion in enumerate(suggestions[:10], 1):
            result_parts.append(
                f"{i}. Bind '{suggestion['label1']}' ({suggestion['id1']}) "
                f"with '{suggestion['label2']}' ({suggestion['id2']})"
            )
            result_parts.append(f"   Score: {suggestion['score']}/100")
            result_parts.append(f"   Reasons: {', '.join(suggestion['reasons'])}")
            result_parts.append(
                f"   → To bind: bind_nodes(node_ids=['{suggestion['id1']}', '{suggestion['id2']}'])"
            )
            result_parts.append("")
        
        if len(suggestions) > 10:
            result_parts.append(f"... and {len(suggestions) - 10} more suggestions with lower scores")
        
        result_parts.append(
            "\n✨ TIP: After binding, use move_shape() on just ONE node - "
            "all bound nodes move automatically!"
        )
    
    return [TextContent(type="text", text="\n".join(result_parts))]


def handle_detect_overlaps(arguments: Any) -> list[TextContent]:
    """Handle detect_overlaps tool call."""
    if diagram_state.current_xml:
        cells = get_cells_from_xml(diagram_state.current_xml)
    elif diagram_state.current_diagram:
        xml_content = diagram_state.current_diagram.to_drawio_xml()
        cells = get_cells_from_xml(xml_content)
    else:
        return [TextContent(
            type="text",
            text="No diagram available. Create a new diagram or load an existing one."
        )]

    results = detect_overlaps(cells)
    node_overlaps = results["node_overlaps"]
    out_of_container = results["out_of_container"]

    total = len(node_overlaps) + len(out_of_container)

    if total == 0:
        return [TextContent(
            type="text",
            text="✓ No overlaps or boundary violations detected. All shapes are correctly positioned!"
        )]

    result_parts = [f"Detected {total} overlap/boundary issue(s):\n"]

    if node_overlaps:
        result_parts.append(f"── Node–Node Overlaps ({len(node_overlaps)}) ──")
        for i, item in enumerate(node_overlaps, 1):
            result_parts.append(f"\n{i}. {item['suggestion']}")
            result_parts.append(
                f"   → Fix: move_shape(shape_id='{item['shape2_id']}', new_x=..., new_y=...)"
            )

    if out_of_container:
        result_parts.append(f"\n── Out-of-Container Violations ({len(out_of_container)}) ──")
        for i, item in enumerate(out_of_container, 1):
            result_parts.append(f"\n{i}. {item['suggestion']}")
            result_parts.append(
                f"   → Fix: move_shape or update_cell to reposition '{item['shape_id']}' "
                f"inside '{item['container_id']}'"
            )

    result_parts.append(
        "\n✨ TIP: Fix overlaps before adding connections to avoid crossing lines."
    )

    return [TextContent(type="text", text="\n".join(result_parts))]
