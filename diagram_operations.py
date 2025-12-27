"""
ID-based diagram operations for editing existing diagrams

Provides functionality to update, add, and delete cells in a draw.io diagram
using DOM manipulation for precise control.
"""

from typing import List, Dict, Any, Optional
from xml.dom import minidom


class OperationError:
    """Represents an error that occurred during a diagram operation"""
    def __init__(self, op_type: str, cell_id: str, message: str):
        self.type = op_type
        self.cell_id = cell_id
        self.message = message


class DiagramOperation:
    """Represents a single diagram operation"""
    def __init__(self, operation: str, cell_id: str, new_xml: Optional[str] = None):
        self.operation = operation  # "update", "add", or "delete"
        self.cell_id = cell_id
        self.new_xml = new_xml


def apply_diagram_operations(xml_content: str, operations: List[DiagramOperation]) -> Dict[str, Any]:
    """
    Apply diagram operations (update/add/delete) using ID-based lookup.
    
    Args:
        xml_content: The full mxfile XML content
        operations: List of operations to apply
        
    Returns:
        Dictionary with 'result' (modified XML) and 'errors' (list of OperationError)
    """
    errors: List[OperationError] = []
    
    try:
        # Parse the XML
        doc = minidom.parseString(xml_content)
    except Exception as e:
        return {
            'result': xml_content,
            'errors': [OperationError('parse', '', f'XML parse error: {str(e)}')]
        }
    
    # Find the root element (inside mxGraphModel)
    root_elements = doc.getElementsByTagName('root')
    if not root_elements:
        return {
            'result': xml_content,
            'errors': [OperationError('parse', '', 'Could not find <root> element in XML')]
        }
    
    root = root_elements[0]
    
    # Build a map of cell IDs to elements
    cell_map: Dict[str, Any] = {}
    for cell in root.getElementsByTagName('mxCell'):
        cell_id = cell.getAttribute('id')
        if cell_id:
            cell_map[cell_id] = cell
    
    # Process each operation
    for op in operations:
        if op.operation == 'update':
            if op.cell_id not in cell_map:
                errors.append(OperationError('update', op.cell_id, f'Cell with id="{op.cell_id}" not found'))
                continue
            
            if not op.new_xml:
                errors.append(OperationError('update', op.cell_id, 'new_xml is required for update operation'))
                continue
            
            try:
                # Parse the new XML
                new_doc = minidom.parseString(f'<wrapper>{op.new_xml}</wrapper>')
                new_cells = new_doc.getElementsByTagName('mxCell')
                if not new_cells:
                    errors.append(OperationError('update', op.cell_id, 'new_xml must contain an mxCell element'))
                    continue
                
                new_cell = new_cells[0]
                new_cell_id = new_cell.getAttribute('id')
                
                if new_cell_id != op.cell_id:
                    errors.append(OperationError('update', op.cell_id, 
                        f'ID mismatch: cell_id is "{op.cell_id}" but new_xml has id="{new_cell_id}"'))
                    continue
                
                # Import and replace the node
                existing_cell = cell_map[op.cell_id]
                imported_node = doc.importNode(new_cell, True)
                existing_cell.parentNode.replaceChild(imported_node, existing_cell)
                
                # Update the map
                cell_map[op.cell_id] = imported_node
                
            except Exception as e:
                errors.append(OperationError('update', op.cell_id, f'Failed to parse new_xml: {str(e)}'))
        
        elif op.operation == 'add':
            if op.cell_id in cell_map:
                errors.append(OperationError('add', op.cell_id, f'Cell with id="{op.cell_id}" already exists'))
                continue
            
            if not op.new_xml:
                errors.append(OperationError('add', op.cell_id, 'new_xml is required for add operation'))
                continue
            
            try:
                # Parse the new XML
                new_doc = minidom.parseString(f'<wrapper>{op.new_xml}</wrapper>')
                new_cells = new_doc.getElementsByTagName('mxCell')
                if not new_cells:
                    errors.append(OperationError('add', op.cell_id, 'new_xml must contain an mxCell element'))
                    continue
                
                new_cell = new_cells[0]
                new_cell_id = new_cell.getAttribute('id')
                
                if new_cell_id != op.cell_id:
                    errors.append(OperationError('add', op.cell_id,
                        f'ID mismatch: cell_id is "{op.cell_id}" but new_xml has id="{new_cell_id}"'))
                    continue
                
                # Import and append the node
                imported_node = doc.importNode(new_cell, True)
                root.appendChild(imported_node)
                
                # Add to map
                cell_map[op.cell_id] = imported_node
                
            except Exception as e:
                errors.append(OperationError('add', op.cell_id, f'Failed to parse new_xml: {str(e)}'))
        
        elif op.operation == 'delete':
            if op.cell_id not in cell_map:
                errors.append(OperationError('delete', op.cell_id, f'Cell with id="{op.cell_id}" not found'))
                continue
            
            # Check for edges referencing this cell (warning only)
            for cell in root.getElementsByTagName('mxCell'):
                if cell.getAttribute('source') == op.cell_id or cell.getAttribute('target') == op.cell_id:
                    edge_id = cell.getAttribute('id')
                    print(f'Warning: Deleting cell "{op.cell_id}" which is referenced by edge "{edge_id}"')
            
            # Remove the node
            existing_cell = cell_map[op.cell_id]
            existing_cell.parentNode.removeChild(existing_cell)
            del cell_map[op.cell_id]
    
    # Serialize back to string
    result = doc.toxml()
    
    return {
        'result': result,
        'errors': errors
    }


def extract_cells_info(xml_content: str) -> List[Dict[str, str]]:
    """
    Extract information about all cells in a diagram
    
    Args:
        xml_content: The full mxfile XML content
        
    Returns:
        List of dictionaries with cell information (id, value, style, etc.)
    """
    try:
        doc = minidom.parseString(xml_content)
    except Exception as e:
        return []
    
    cells_info = []
    for cell in doc.getElementsByTagName('mxCell'):
        cell_id = cell.getAttribute('id')
        if cell_id and cell_id not in ['0', '1']:  # Skip default root cells
            info = {
                'id': cell_id,
                'value': cell.getAttribute('value'),
                'style': cell.getAttribute('style'),
                'vertex': cell.getAttribute('vertex'),
                'edge': cell.getAttribute('edge'),
            }
            cells_info.append(info)
    
    return cells_info
