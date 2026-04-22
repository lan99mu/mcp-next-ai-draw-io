#!/usr/bin/env python3
"""
Batch operation handler.

Executes a list of operations in a single tool call to reduce round-trips
and token consumption compared to calling each tool individually.

Supported operation types (same params as the corresponding single tools):
  - add_shape
  - add_connection
  - bind_nodes
  - unbind_nodes
  - move_shape
  - update_cell
  - delete_cell

Each operation object must have an "op" key plus any parameters required by
that operation.  On completion a compact summary is returned together with
any autosave info.
"""

from typing import Any
from mcp.types import TextContent

from .state import diagram_state
from .cell_handlers import (
    handle_add_shape,
    handle_add_connection,
    handle_update_cell,
    handle_delete_cell,
)
from .binding_handlers import (
    handle_bind_nodes,
    handle_unbind_nodes,
    handle_move_shape,
    handle_auto_layout_adjust,
)

_DEFAULT_SUCCESS_MESSAGE = "ok"

# Dispatch table: op name → handler function
_OP_HANDLERS: dict[str, Any] = {
    "add_shape": handle_add_shape,
    "add_connection": handle_add_connection,
    "bind_nodes": handle_bind_nodes,
    "unbind_nodes": handle_unbind_nodes,
    "move_shape": handle_move_shape,
    "update_cell": handle_update_cell,
    "delete_cell": handle_delete_cell,
    "auto_layout_adjust": handle_auto_layout_adjust,
}


def handle_batch_operations(arguments: Any) -> list[TextContent]:
    """Execute multiple diagram operations in a single call."""
    operations: list[dict] = arguments.get("operations", [])
    if not operations:
        return [TextContent(type="text", text="Error: 'operations' list is required and must not be empty.")]

    results: list[str] = []
    errors: list[str] = []

    for idx, op in enumerate(operations):
        op_name: str = op.get("op", "")
        handler = _OP_HANDLERS.get(op_name)
        if handler is None:
            errors.append(f"[{idx}] Unknown op '{op_name}'")
            continue

        # Build per-op arguments (everything except the "op" key itself)
        op_args = {k: v for k, v in op.items() if k != "op"}

        try:
            # Call the underlying handler; it returns list[TextContent]
            response = handler(op_args)
            # Extract the text from the first content item for the summary
            text = response[0].text if response else _DEFAULT_SUCCESS_MESSAGE
            results.append(f"[{idx}] {op_name}: {text}")
        except Exception as exc:
            errors.append(f"[{idx}] {op_name} failed: {exc}")

    # Compose summary
    total = len(operations)
    succeeded = total - len(errors)
    summary_parts = [f"Batch: {succeeded}/{total} succeeded"]
    if results:
        summary_parts.append("\n".join(results))
    if errors:
        summary_parts.append("Errors:\n" + "\n".join(errors))

    return [TextContent(type="text", text="\n".join(summary_parts))]
