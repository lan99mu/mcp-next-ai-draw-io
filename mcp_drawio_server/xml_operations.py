"""
XML parsing and manipulation operations for Draw.io files.

This module provides functions for parsing, reading, and modifying
Draw.io XML structures.
"""

from xml.dom import minidom


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
                
                cells.append(cell_info)
        
        return cells
    except Exception as e:
        # Log error and return empty list
        print(f"Warning: Failed to parse XML for cells: {str(e)}")
        return []


def update_cell_in_xml(xml_content: str, cell_id: str, **updates) -> str:
    """Update a cell in the XML by ID"""
    try:
        doc = parse_drawio_xml(xml_content)
        
        # Find the cell
        for cell in doc.getElementsByTagName('mxCell'):
            if cell.getAttribute('id') == cell_id:
                # Update attributes
                if 'value' in updates and updates['value'] is not None:
                    cell.setAttribute('value', str(updates['value']))
                if 'style' in updates and updates['style'] is not None:
                    cell.setAttribute('style', str(updates['style']))
                
                # Update geometry
                geom_elements = cell.getElementsByTagName('mxGeometry')
                if geom_elements and any(k in updates for k in ['x', 'y', 'width', 'height']):
                    geom = geom_elements[0]
                    if 'x' in updates and updates['x'] is not None:
                        geom.setAttribute('x', str(updates['x']))
                    if 'y' in updates and updates['y'] is not None:
                        geom.setAttribute('y', str(updates['y']))
                    if 'width' in updates and updates['width'] is not None:
                        geom.setAttribute('width', str(updates['width']))
                    if 'height' in updates and updates['height'] is not None:
                        geom.setAttribute('height', str(updates['height']))
                
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
