#!/usr/bin/env python3
"""
Test new file loading and modification capabilities
"""

import tempfile
from pathlib import Path
from mcp_drawio_server import (
    Diagram, 
    get_cells_from_xml, 
    update_cell_in_xml, 
    delete_cell_in_xml
)


def test_load_and_modify():
    """Test loading and modifying an existing diagram"""
    print("Testing load and modify functionality...")
    
    # Create a test diagram
    diagram = Diagram(name="Test Diagram")
    shape1 = diagram.add_shape("Shape 1", x=100, y=100)
    shape2 = diagram.add_shape("Shape 2", x=250, y=100)
    conn = diagram.add_connection(shape1, shape2, label="Connection")
    
    # Get XML
    xml_content = diagram.to_drawio_xml()
    print(f"✓ Created diagram with {len(diagram.shapes)} shapes")
    
    # Parse cells from XML
    cells = get_cells_from_xml(xml_content)
    print(f"✓ Parsed {len(cells)} cells from XML")
    
    # Verify cells
    assert len(cells) == 3  # 2 shapes + 1 connection
    shapes = [c for c in cells if c['vertex']]
    edges = [c for c in cells if c['edge']]
    assert len(shapes) == 2
    assert len(edges) == 1
    print(f"✓ Found {len(shapes)} shapes and {len(edges)} edges")
    
    # Update a cell
    shape1_id = shape1
    updated_xml = update_cell_in_xml(xml_content, shape1_id, value="Updated Label", x=150)
    print(f"✓ Updated cell {shape1_id}")
    
    # Verify update
    updated_cells = get_cells_from_xml(updated_xml)
    updated_shape = next(c for c in updated_cells if c['id'] == shape1_id)
    assert updated_shape['value'] == "Updated Label"
    assert updated_shape['x'] == "150"
    print("✓ Verified cell update")
    
    # Delete a cell
    deleted_xml = delete_cell_in_xml(updated_xml, conn)
    print(f"✓ Deleted connection {conn}")
    
    # Verify deletion
    final_cells = get_cells_from_xml(deleted_xml)
    assert len(final_cells) == 2  # Only shapes remain
    assert all(c['vertex'] for c in final_cells)
    print("✓ Verified cell deletion")
    
    # Save to file
    tmp_dir = Path(tempfile.gettempdir())
    test_file = tmp_dir / "test_modified.drawio"
    test_file.write_text(deleted_xml, encoding='utf-8')
    print(f"✓ Saved modified diagram to: {test_file}")
    
    # Load from file
    loaded_xml = test_file.read_text(encoding='utf-8')
    loaded_cells = get_cells_from_xml(loaded_xml)
    assert len(loaded_cells) == 2
    print(f"✓ Loaded diagram from file, verified {len(loaded_cells)} cells")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Draw.io Server - File Operations Test")
    print("=" * 60)
    
    try:
        test_load_and_modify()
        
        print("\n" + "=" * 60)
        print("✓ All file operation tests passed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
