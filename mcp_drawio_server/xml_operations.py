"""
XML parsing and manipulation operations for Draw.io diagrams.

This module provides functions for parsing, reading, and modifying
Draw.io XML structures.
"""

from typing import Optional
from xml.dom import minidom

from .diagram import coerce_html_label


def _is_non_empty_string(value: Optional[str]) -> bool:
    """Return True when an XML attribute contains a non-empty string value."""
    return value is not None and value != ''


def _format_html_value(value: str) -> str:
    """Normalize multiline labels into Draw.io HTML label format.

    Accepts plain text (``\\n``), GraphViz style (``\\l``) or already-HTML
    labels and consistently emits ``<br>`` line breaks so every label the
    server writes back is HTML-style.
    """
    return coerce_html_label(value)


def parse_drawio_xml(xml_content: str) -> minidom.Document:
    """Parse Draw.io XML and return DOM document"""
    return minidom.parseString(xml_content)


def get_cells_from_xml(xml_content: str) -> list[dict]:
    """Extract all cells from Draw.io XML"""
    try:
        doc = parse_drawio_xml(xml_content)
        cells = []
        
        for cell in doc.getElementsByTagName('mxCell'):
            cell_id = cell.getAttribute('id')
            if cell_id and cell_id not in ['0', '1']:  # Skip default root cells
                cell_info = {
                    'id': cell_id,
                    'value': cell.getAttribute('value'),
                    'style': cell.getAttribute('style'),
                    'vertex': cell.getAttribute('vertex') == '1',
                    'edge': cell.getAttribute('edge') == '1',
                    'parent': cell.getAttribute('parent'),
                    'source': cell.getAttribute('source'),
                    'target': cell.getAttribute('target'),
                }
                
                # Get bound_nodes if available
                bound_nodes_attr = cell.getAttribute('bound_nodes')
                if bound_nodes_attr:
                    cell_info['bound_nodes'] = bound_nodes_attr.split(',')
                else:
                    cell_info['bound_nodes'] = []
                
                # Get geometry if available
                geom = cell.getElementsByTagName('mxGeometry')
                if geom:
                    g = geom[0]
                    cell_info['x'] = g.getAttribute('x')
                    cell_info['y'] = g.getAttribute('y')
                    cell_info['width'] = g.getAttribute('width')
                    cell_info['height'] = g.getAttribute('height')
                    
                    # Get entry/exit points for edges
                    if cell_info['edge']:
                        entry_x = g.getAttribute('entryX')
                        entry_y = g.getAttribute('entryY')
                        exit_x = g.getAttribute('exitX')
                        exit_y = g.getAttribute('exitY')

                        if entry_x:
                            cell_info['entry_x'] = entry_x
                        if entry_y:
                            cell_info['entry_y'] = entry_y
                        if exit_x:
                            cell_info['exit_x'] = exit_x
                        if exit_y:
                            cell_info['exit_y'] = exit_y

                        geometry_points = []
                        if _is_non_empty_string(entry_x) or _is_non_empty_string(entry_y):
                            geometry_points.append({
                                'type': 'entry',
                                'x': entry_x,
                                'y': entry_y,
                            })
                        if _is_non_empty_string(exit_x) or _is_non_empty_string(exit_y):
                            geometry_points.append({
                                'type': 'exit',
                                'x': exit_x,
                                'y': exit_y,
                            })
                        
                        # Get waypoints (Array of mxPoint elements)
                        arrays = g.getElementsByTagName('Array')
                        for arr in arrays:
                            if arr.getAttribute('as') == 'points':
                                waypoints = []
                                for point in arr.getElementsByTagName('mxPoint'):
                                    x = point.getAttribute('x')
                                    y = point.getAttribute('y')
                                    if x and y:
                                        waypoints.append([x, y])
                                        geometry_points.append({
                                            'type': 'waypoint',
                                            'x': x,
                                            'y': y,
                                        })
                                if waypoints:
                                    cell_info['waypoints'] = waypoints
                        
                        # Get source/target points
                        for point in g.getElementsByTagName('mxPoint'):
                            point_as = point.getAttribute('as')
                            if point_as == 'sourcePoint':
                                x = point.getAttribute('x')
                                y = point.getAttribute('y')
                                if x and y:
                                    cell_info['source_point'] = [x, y]
                                    geometry_points.append({
                                        'type': 'sourcePoint',
                                        'x': x,
                                        'y': y,
                                    })
                            elif point_as == 'targetPoint':
                                x = point.getAttribute('x')
                                y = point.getAttribute('y')
                                if x and y:
                                    cell_info['target_point'] = [x, y]
                                    geometry_points.append({
                                        'type': 'targetPoint',
                                        'x': x,
                                        'y': y,
                                    })
                            # Parse label offset (as="offset") so downstream
                            # consumers (e.g. overlap detection) can position
                            # the edge label relative to its anchor on the
                            # routed polyline.
                            elif point_as == 'offset':
                                x = point.getAttribute('x')
                                y = point.getAttribute('y')
                                if x or y:
                                    try:
                                        cell_info['label_offset_x'] = float(x) if x else 0.0
                                        cell_info['label_offset_y'] = float(y) if y else 0.0
                                    except (TypeError, ValueError):
                                        pass
                        if geometry_points:
                            cell_info['geometry_points'] = geometry_points
                
                cells.append(cell_info)
        
        return cells
    except Exception as e:
        # Log error and return empty list
        print(f"Warning: Failed to parse XML for cells: {str(e)}")
        return []


def update_cell_in_xml(xml_content: str, cell_id: str, **updates) -> str:
    """Update a cell in the XML by ID.

    Supports the following keys:
      value, style                         — attributes on <mxCell>
      x, y, width, height                  — attributes on <mxGeometry>
      entry_x, entry_y, exit_x, exit_y     — edge anchor attrs on <mxGeometry>
      waypoints                            — list[(x, y)] writing/replacing
                                              the nested <Array as="points">
    """
    try:
        doc = parse_drawio_xml(xml_content)

        # Find the cell
        for cell in doc.getElementsByTagName('mxCell'):
            if cell.getAttribute('id') == cell_id:
                # Update attributes
                if 'value' in updates and updates['value'] is not None:
                    cell.setAttribute('value', _format_html_value(str(updates['value'])))
                if 'style' in updates and updates['style'] is not None:
                    cell.setAttribute('style', str(updates['style']))

                geom_elements = cell.getElementsByTagName('mxGeometry')
                geom_keys = {'x', 'y', 'width', 'height',
                             'entry_x', 'entry_y', 'exit_x', 'exit_y', 'waypoints'}
                if geom_elements and any(k in updates for k in geom_keys):
                    geom = geom_elements[0]
                    for attr, key in (
                        ('x', 'x'), ('y', 'y'),
                        ('width', 'width'), ('height', 'height'),
                        ('entryX', 'entry_x'), ('entryY', 'entry_y'),
                        ('exitX', 'exit_x'), ('exitY', 'exit_y'),
                    ):
                        if key in updates and updates[key] is not None:
                            geom.setAttribute(attr, str(updates[key]))

                    # Waypoints — replace the existing Array as="points" with a
                    # fresh list, or create one if missing.
                    if 'waypoints' in updates and updates['waypoints'] is not None:
                        waypoints = updates['waypoints']
                        # Remove any existing waypoint array.
                        for arr in list(geom.getElementsByTagName('Array')):
                            if arr.getAttribute('as') == 'points':
                                arr.parentNode.removeChild(arr)
                        if waypoints:
                            array = doc.createElement('Array')
                            array.setAttribute('as', 'points')
                            for wp in waypoints:
                                if not wp or len(wp) < 2:
                                    continue
                                point = doc.createElement('mxPoint')
                                point.setAttribute('x', str(wp[0]))
                                point.setAttribute('y', str(wp[1]))
                                array.appendChild(point)
                            geom.appendChild(array)

                # Update label offset (nested mxPoint as="offset").
                if any(k in updates for k in ('label_offset_x', 'label_offset_y')):
                    if geom_elements:
                        geom = geom_elements[0]
                        offset_el = None
                        for point in geom.getElementsByTagName('mxPoint'):
                            if point.getAttribute('as') == 'offset':
                                offset_el = point
                                break
                        if offset_el is None:
                            offset_el = doc.createElement('mxPoint')
                            offset_el.setAttribute('as', 'offset')
                            geom.appendChild(offset_el)
                        if updates.get('label_offset_x') is not None:
                            offset_el.setAttribute('x', str(updates['label_offset_x']))
                        elif not offset_el.getAttribute('x'):
                            offset_el.setAttribute('x', '0')
                        if updates.get('label_offset_y') is not None:
                            offset_el.setAttribute('y', str(updates['label_offset_y']))
                        elif not offset_el.getAttribute('y'):
                            offset_el.setAttribute('y', '0')

                break

        return doc.toxml()
    except Exception as e:
        raise ValueError(f"Failed to update cell: {str(e)}")


def delete_cell_in_xml(xml_content: str, cell_id: str) -> str:
    """Delete a cell from the XML by ID"""
    try:
        doc = parse_drawio_xml(xml_content)
        
        # Find and remove the cell
        for cell in doc.getElementsByTagName('mxCell'):
            if cell.getAttribute('id') == cell_id:
                cell.parentNode.removeChild(cell)
                break
        
        return doc.toxml()
    except Exception as e:
        raise ValueError(f"Failed to delete cell: {str(e)}")
