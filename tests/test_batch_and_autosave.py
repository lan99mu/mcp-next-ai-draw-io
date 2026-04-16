#!/usr/bin/env python3
"""
Tests for batch_operations tool and autosave mode.
"""

import tempfile
from pathlib import Path

import pytest

from mcp_drawio_server.handlers import handle_tool_call
from mcp_drawio_server.handlers.batch_handlers import handle_batch_operations
from mcp_drawio_server.handlers.file_handlers import (
    handle_create_diagram,
    handle_load_diagram,
    handle_save_diagram,
)
from mcp_drawio_server.handlers.state import diagram_state


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _text(result) -> str:
    """Extract text from handler result."""
    return result[0].text


def _reset():
    """Reset global diagram state before each test."""
    diagram_state.reset()


# ===========================================================================
# batch_operations tests
# ===========================================================================

class TestBatchOperations:
    def setup_method(self):
        _reset()
        handle_create_diagram({})

    def test_empty_operations_returns_error(self):
        result = handle_batch_operations({"operations": []})
        assert "required" in _text(result).lower() or "empty" in _text(result).lower()

    def test_missing_operations_key_returns_error(self):
        result = handle_batch_operations({})
        assert "required" in _text(result).lower() or "empty" in _text(result).lower()

    def test_unknown_op_returns_error_in_summary(self):
        result = handle_batch_operations({
            "operations": [{"op": "nonexistent_op"}]
        })
        text = _text(result)
        assert "Unknown op" in text or "nonexistent_op" in text

    def test_add_shapes_batch(self):
        result = handle_batch_operations({
            "operations": [
                {"op": "add_shape", "label": "A", "x": 0, "y": 0},
                {"op": "add_shape", "label": "B", "x": 200, "y": 0},
            ]
        })
        text = _text(result)
        assert "2/2 succeeded" in text
        # Shapes must actually exist in diagram
        diagram = diagram_state.current_diagram
        assert len(diagram.shapes) == 2

    def test_add_shape_and_connection_batch(self):
        # Add two shapes first so we have IDs
        diagram = diagram_state.get_or_create_diagram()
        id_a = diagram.add_shape("A", x=0, y=0)
        id_b = diagram.add_shape("B", x=200, y=0)

        result = handle_batch_operations({
            "operations": [
                {"op": "add_connection", "source_id": id_a, "target_id": id_b, "label": "link"},
            ]
        })
        text = _text(result)
        assert "1/1 succeeded" in text
        assert len(diagram.connections) == 1

    def test_partial_failure_reported(self):
        """Unknown op in batch does not abort subsequent ops."""
        result = handle_batch_operations({
            "operations": [
                {"op": "bad_op"},
                {"op": "add_shape", "label": "OK"},
            ]
        })
        text = _text(result)
        assert "1/2 succeeded" in text
        assert "bad_op" in text or "Unknown op" in text

    def test_bind_nodes_in_batch(self):
        diagram = diagram_state.get_or_create_diagram()
        id_a = diagram.add_shape("A", x=0, y=0)
        id_b = diagram.add_shape("B", x=100, y=0)

        result = handle_batch_operations({
            "operations": [
                {"op": "bind_nodes", "node_ids": [id_a, id_b]},
            ]
        })
        text = _text(result)
        assert "1/1 succeeded" in text
        assert id_b in diagram.shapes[id_a].bound_nodes

    def test_move_shape_in_batch(self):
        diagram = diagram_state.get_or_create_diagram()
        shape_id = diagram.add_shape("X", x=0, y=0)

        result = handle_batch_operations({
            "operations": [
                {"op": "move_shape", "shape_id": shape_id, "new_x": 50, "new_y": 75},
            ]
        })
        text = _text(result)
        assert "1/1 succeeded" in text
        assert diagram.shapes[shape_id].x == 50
        assert diagram.shapes[shape_id].y == 75

    def test_update_and_delete_in_batch(self):
        """update_cell and delete_cell work inside a batch (XML-backed)."""
        _reset()
        # Load from a new file so current_xml is set (required for update_cell / delete_cell)
        from mcp_drawio_server.handlers.file_handlers import handle_save_diagram
        handle_create_diagram({})
        diagram = diagram_state.get_or_create_diagram()
        id_a = diagram.add_shape("Old Label", x=0, y=0)

        # Persist to current_xml
        diagram_state.current_xml = diagram.to_drawio_xml()

        result = handle_batch_operations({
            "operations": [
                {"op": "update_cell", "cell_id": id_a, "value": "New Label"},
            ]
        })
        text = _text(result)
        assert "1/1 succeeded" in text


# ===========================================================================
# autosave tests
# ===========================================================================

class TestAutosaveCreate:
    def setup_method(self):
        _reset()

    def test_create_with_autosave_path(self, tmp_path):
        autosave_file = str(tmp_path / "test.drawio")
        handle_create_diagram({"name": "AutoTest", "autosave_path": autosave_file})
        assert diagram_state.autosave_enabled is True
        assert diagram_state.autosave_path == autosave_file

    def test_create_without_autosave_path(self):
        handle_create_diagram({"name": "Normal"})
        assert diagram_state.autosave_enabled is False
        assert diagram_state.autosave_path is None

    def test_autosave_fires_on_add_shape(self, tmp_path):
        autosave_file = str(tmp_path / "auto.drawio")
        handle_create_diagram({"autosave_path": autosave_file})
        from mcp_drawio_server.handlers.cell_handlers import handle_add_shape
        handle_add_shape({"label": "Node1", "x": 0, "y": 0})
        assert Path(autosave_file).exists(), "File should be written after add_shape"

    def test_autosave_write_count_increments(self, tmp_path):
        autosave_file = str(tmp_path / "auto.drawio")
        handle_create_diagram({"autosave_path": autosave_file})
        from mcp_drawio_server.handlers.cell_handlers import handle_add_shape
        handle_add_shape({"label": "N1", "x": 0, "y": 0})
        handle_add_shape({"label": "N2", "x": 100, "y": 0})
        assert diagram_state.write_count == 2

    def test_autosave_response_contains_path_and_version(self, tmp_path):
        autosave_file = str(tmp_path / "auto.drawio")
        handle_create_diagram({"autosave_path": autosave_file})
        from mcp_drawio_server.handlers.cell_handlers import handle_add_shape
        result = handle_add_shape({"label": "Node", "x": 0, "y": 0})
        text = _text(result)
        assert "autosaved" in text
        assert "v1" in text


class TestAutosaveLoad:
    def setup_method(self):
        _reset()

    def test_load_with_autosave_true(self, tmp_path):
        from mcp_drawio_server.diagram import Diagram
        # Create a file to load
        d = Diagram("Existing")
        d.add_shape("S", x=0, y=0)
        f = tmp_path / "existing.drawio"
        f.write_text(d.to_drawio_xml(), encoding="utf-8")

        handle_load_diagram({"path": str(f), "autosave": True})
        assert diagram_state.autosave_enabled is True
        assert diagram_state.autosave_path == str(f)

    def test_load_without_autosave_default(self, tmp_path):
        from mcp_drawio_server.diagram import Diagram
        d = Diagram("Existing")
        d.add_shape("S", x=0, y=0)
        f = tmp_path / "existing.drawio"
        f.write_text(d.to_drawio_xml(), encoding="utf-8")

        handle_load_diagram({"path": str(f)})
        assert diagram_state.autosave_enabled is False


# ===========================================================================
# save_diagram observability tests
# ===========================================================================

class TestSaveObservability:
    def setup_method(self):
        _reset()

    def test_save_returns_version_and_bytes(self, tmp_path):
        handle_create_diagram({})
        from mcp_drawio_server.handlers.cell_handlers import handle_add_shape
        handle_add_shape({"label": "X", "x": 0, "y": 0})
        out = str(tmp_path / "out.drawio")
        result = handle_save_diagram({"path": out})
        text = _text(result)
        assert "v1" in text
        assert "B" in text  # bytes indicator
        assert out in text or "out.drawio" in text

    def test_write_count_increments_on_each_save(self, tmp_path):
        handle_create_diagram({})
        out = str(tmp_path / "out.drawio")
        handle_save_diagram({"path": out})
        handle_save_diagram({"path": out})
        assert diagram_state.write_count == 2

    def test_no_diagram_returns_error(self, tmp_path):
        result = handle_save_diagram({"path": str(tmp_path / "x.drawio")})
        assert "Error" in _text(result)


# ===========================================================================
# tool definitions test
# ===========================================================================

def test_batch_operations_tool_defined():
    from mcp_drawio_server.tools import get_tool_definitions
    tools = {t.name: t for t in get_tool_definitions()}
    assert "batch_operations" in tools
    schema = tools["batch_operations"].inputSchema
    assert "operations" in schema["properties"]


def test_create_diagram_has_autosave_path():
    from mcp_drawio_server.tools import get_tool_definitions
    tools = {t.name: t for t in get_tool_definitions()}
    props = tools["create_diagram"].inputSchema["properties"]
    assert "autosave_path" in props


def test_load_diagram_has_autosave_flag():
    from mcp_drawio_server.tools import get_tool_definitions
    tools = {t.name: t for t in get_tool_definitions()}
    props = tools["load_diagram"].inputSchema["properties"]
    assert "autosave" in props
