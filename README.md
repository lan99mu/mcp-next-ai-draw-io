# MCP Draw.io Server

一个增强版的 Model Context Protocol (MCP) 服务器，使 AI 助手（如 GitHub Copilot、Claude Desktop）能够以编程方式生成和编辑 Draw.io 图表文件，并提供**实时浏览器预览**。

A Python-based Model Context Protocol (MCP) server that enables AI assistants (like GitHub Copilot, Claude Desktop) to generate and edit Draw.io diagram files programmatically with **real-time browser preview**.

## 🎯 主要改进 / Key Improvements

相比基础 MCP 服务器，此版本参考 [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io) 项目，增加了以下重要功能：

Compared to basic MCP servers, this version is inspired by [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io) and adds:

- 🌐 **实时浏览器预览** / **Real-time Browser Preview** - 内置 HTTP 服务器，在浏览器中实时显示图表更新
- ✏️ **图表编辑功能** / **Diagram Editing** - 支持基于 ID 的更新、添加、删除操作
- 📜 **版本历史** / **Version History** - 自动保存图表历史版本
- 💾 **导出功能** / **Export to File** - 直接导出为 .drawio 文件
- 🔄 **状态同步** / **State Synchronization** - AI 与浏览器状态自动同步

## Features

- ✍️ **Generate Draw.io XML files** - Create .drawio diagram files programmatically
- 🌐 **Real-time browser preview** - See your diagrams update live in the browser
- 🔷 **Multiple shape types** - Support for rectangle, ellipse, diamond, and more
- ✏️ **Edit existing diagrams** - Update, add, or delete diagram elements by ID
- 🔗 **Connect shapes** - Add connections between shapes with customizable arrows
- 📜 **Version history** - Track and restore previous diagram versions
- 💾 **Export to files** - Save diagrams as .drawio files
- 💾 **Standard Draw.io format** - Output compatible with Draw.io and diagrams.net
- 🤖 **MCP-compatible** - Works with VS Code Copilot, Claude Desktop, and other MCP clients
- 📦 **Lightweight** - Simple Python implementation with minimal dependencies

**Enhanced Workflow:** Unlike the basic version that only generates XML, this version provides a complete workflow:
1. **Start Session** → Opens browser for real-time preview
2. **Create/Edit Diagrams** → See changes instantly in browser
3. **Export** → Save to .drawio files

**Note:** This server generates AND displays Draw.io files in real-time. The generated files can also be opened in Draw.io (VS Code extension or web app) for further editing.

## Installation

### Prerequisites

- Python 3.10 or higher
- VS Code with Draw.io extension installed
- MCP-compatible client (e.g., Claude Desktop, VS Code Copilot)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/lan99mu/mcp-next-ai-draw-io.git
cd mcp-next-ai-draw-io
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using the project in development mode:
```bash
pip install -e .
```

## Configuration

### For VS Code Copilot

Add the following to your MCP settings configuration file:

**On macOS/Linux**: `~/.config/mcp/settings.json`
**On Windows**: `%APPDATA%\mcp\settings.json`

```json
{
  "mcpServers": {
    "drawio": {
      "command": "python",
      "args": ["/path/to/mcp-next-ai-draw-io/mcp_drawio_server.py"]
    }
  }
}
```

### For Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "drawio": {
      "command": "python",
      "args": ["/path/to/mcp-next-ai-draw-io/mcp_drawio_server.py"]
    }
  }
}
```

## Usage

Once configured, you can ask your AI assistant to create diagrams. Here are some example prompts:

### Creating a Simple Flowchart

```
Create a flowchart for a user login process:
1. Start
2. Enter credentials
3. Validate (diamond shape)
4. If valid, go to dashboard
5. If invalid, show error
```

### Creating a System Architecture Diagram

```
Create a system architecture diagram with:
- A web browser (client)
- A load balancer
- Three API servers
- A database
Connect them appropriately.
```

### Creating an ER Diagram

```
Create an entity-relationship diagram for a blog system:
- User entity (rectangle)
- Post entity (rectangle)
- Comment entity (rectangle)
Connect them with appropriate relationships.
```

## Available Tools

The MCP server provides the following tools:

### `start_session`
**NEW!** Start a new diagram session with real-time browser preview.
- Opens a browser window that shows diagram updates in real-time
- Should be called first before creating or editing diagrams
- Starts an embedded HTTP server (default port: 6002)

### `create_diagram`
Create a new Draw.io diagram.
- **Parameters:**
  - `name` (optional): Name of the diagram (default: "Untitled")
- Resets any existing diagram
- Use `display_diagram` afterwards to show it in the browser

### `add_shape`
Add a shape/node to the diagram.
- **Parameters:**
  - `label` (required): Label text for the shape
  - `x` (optional): X coordinate (default: 0)
  - `y` (optional): Y coordinate (default: 0)
  - `width` (optional): Width of the shape (default: 120)
  - `height` (optional): Height of the shape (default: 60)
  - `shape_type` (optional): Type of shape - `rectangle`, `ellipse`, `diamond`, `parallelogram`, `hexagon`, `cylinder`, `cloud` (default: "rectangle")
  - `style` (optional): Custom Draw.io style string

### `add_connection`
Add a connection/edge between two shapes.
- **Parameters:**
  - `source_id` (required): ID of the source shape
  - `target_id` (required): ID of the target shape
  - `label` (optional): Label text for the connection
  - `arrow_type` (optional): Arrow type - `classic`, `block`, `open`, `oval`, `diamond`, `none` (default: "classic")
  - `style` (optional): Custom Draw.io style string

### `display_diagram`
**NEW!** Display the current diagram in the browser.
- Pushes the diagram XML to the browser for real-time preview
- Use this after adding shapes and connections
- Automatically saves to version history

### `edit_diagram`
**NEW!** Edit an existing diagram using ID-based operations.
- **Parameters:**
  - `operations` (required): Array of operations
    - Each operation has:
      - `operation`: "update", "add", or "delete"
      - `cell_id`: The ID of the cell to operate on
      - `new_xml` (for update/add): Complete mxCell XML element
- **Workflow:**
  1. Call `get_diagram` to see current cell IDs
  2. Prepare your operations based on the cell IDs
  3. Call `edit_diagram` with the operations
- Automatically syncs with browser and saves to history

### `get_diagram`
Get the current diagram as Draw.io XML format.
- Fetches the latest state from the browser if a session is active
- Shows cell summary for easier editing
- Can be saved to a .drawio file

### `list_shapes`
List all shapes currently in the diagram with their IDs and labels.

### `export_diagram`
**NEW!** Export the current diagram to a .drawio file.
- **Parameters:**
  - `path` (required): File path to save the diagram (e.g., ./diagram.drawio)
- Automatically adds .drawio extension if missing
- Exports the latest version from browser or current diagram

### `get_history`
**NEW!** Get the version history for the current session.
- Shows how many versions are saved
- History is automatically saved when you display or edit diagrams

## Example Workflow

### Basic Workflow (Real-time Preview) - Recommended!

1. **Start a session with browser preview**
   ```
   Ask AI: "Start a new Draw.io session with browser preview"
   → AI calls start_session tool
   → Browser opens showing real-time preview
   ```

2. **Create a diagram**
   ```
   Ask AI: "Create a flowchart for user login process"
   → AI calls create_diagram, add_shape, add_connection
   → AI calls display_diagram
   → You see the diagram appear in your browser immediately!
   ```

3. **Edit the diagram**
   ```
   Ask AI: "Change the color of the login button to blue"
   → AI calls get_diagram to see current cell IDs
   → AI calls edit_diagram to update the specific cell
   → Browser updates automatically
   ```

4. **Export the final result**
   ```
   Ask AI: "Export this diagram to login-flow.drawio"
   → AI calls export_diagram
   → File saved to disk
   ```

### Traditional Workflow (Without Browser)

If you don't start a session, the server works like the basic version:

1. **Start a conversation with your AI assistant** in VS Code or Claude Desktop
2. **Request a diagram**: "Create a flowchart for processing an order"
3. **The AI will use the MCP tools** to:
   - Create a new diagram
   - Add shapes for each step
   - Connect them with arrows
   - Return the Draw.io XML
4. **Save the output** to a `.drawio` file
5. **Open in Draw.io** extension in VS Code or the Draw.io desktop app

## Output Format

The server generates diagrams in Draw.io XML format, which can be:
- **Displayed in real-time** in your browser (with session)
- Saved as `.drawio` files
- Opened in VS Code with the Draw.io extension
- Opened in the Draw.io desktop application
- Opened at https://app.diagrams.net/

## Development

### Running Tests

```bash
pytest
```

### Project Structure

```
mcp-next-ai-draw-io/
├── mcp_drawio_server.py     # Main MCP server implementation
├── http_server.py            # Embedded HTTP server for browser preview
├── diagram_operations.py     # ID-based diagram editing operations
├── history.py                # Version history management
├── pyproject.toml            # Project configuration
├── requirements.txt          # Python dependencies
├── test_functionality.py     # Functionality tests
└── README.md                # This file
```

## How It Works

### Real-time Preview Architecture

```
┌─────────────────┐     MCP      ┌─────────────────┐
│  AI Assistant   │ ◄──────────► │   MCP Server    │
│ (Copilot/Claude)│   (stdio)    │  (this package) │
└─────────────────┘              └────────┬────────┘
                                          │
                                 ┌────────▼────────┐
                                 │ Embedded HTTP   │
                                 │ Server (:6002)  │
                                 └────────┬────────┘
                                          │
                                 ┌────────▼────────┐
                                 │  User's Browser │
                                 │ (draw.io embed) │
                                 └─────────────────┘
```

1. **MCP Server** receives tool calls from AI via stdio
2. **Embedded HTTP Server** serves the draw.io UI and manages diagram state
3. **Browser** shows real-time diagram updates via polling (1-second intervals)
4. **State Synchronization** ensures AI and browser stay in sync
5. **Version History** automatically saves each diagram change

### Traditional Mode (Without Session)

1. The MCP server runs as a background process
2. It communicates with MCP clients (like VS Code Copilot) via stdio
3. When prompted, the AI assistant calls the server's tools to:
   - Create diagram structures in memory
   - Add shapes and connections
   - Generate Draw.io-compatible XML
4. The generated XML can be saved to a `.drawio` file
5. Open the file in Draw.io (VS Code extension, desktop app, or web) to view and edit

**Key Difference:** 
- **With session (recommended)**: Real-time preview in browser, full editing capabilities, version history
- **Without session**: Only generates XML files, no visual feedback until opened in Draw.io

## Supported Shape Types

### Predefined Shapes (for convenience)

The server provides 7 commonly-used predefined shape types:

- **rectangle**: Standard rectangular box
- **ellipse**: Circular/oval shape
- **diamond**: Diamond shape (often used for decision points)
- **parallelogram**: Parallelogram shape (often used for input/output)
- **hexagon**: Hexagon shape (often used for preparation steps)
- **cylinder**: Cylinder shape (often used for databases)
- **cloud**: Cloud shape (often used for cloud services)

### All Draw.io Shapes (via custom styles)

**The server supports ALL Draw.io shapes** through the `style` parameter. You can use any Draw.io shape by providing a custom style string:

```python
# Examples of using custom Draw.io shapes:

# Actor/Person shape (UML)
add_shape(label="User", style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;")

# Database/Datastore shape
add_shape(label="MySQL", style="shape=datastore;whiteSpace=wrap;html=1;")

# Document shape
add_shape(label="Report", style="shape=document;whiteSpace=wrap;html=1;")

# Process/Gear shape
add_shape(label="Processing", style="shape=process;whiteSpace=wrap;html=1;backgroundOutline=1;")

# Arrow shape
add_shape(label="Direction", style="shape=singleArrow;whiteSpace=wrap;html=1;")

# And hundreds more...
```

To find the style string for any Draw.io shape:
1. Create the shape in Draw.io
2. Right-click → Edit Style
3. Copy the style string and use it in the `style` parameter

## Troubleshooting

### Server not connecting
- Verify Python 3.10+ is installed: `python --version`
- Check the path in your MCP configuration is correct
- Ensure dependencies are installed: `pip install -r requirements.txt`

### Diagrams not rendering correctly
- Ensure you're saving the output as a `.drawio` file
- Open with Draw.io extension or app
- Check that the XML is complete in the output

### Tool calls not working
- Restart your MCP client (VS Code, Claude Desktop, etc.)
- Check the server logs for errors
- Verify the MCP configuration file is in the correct location

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Acknowledgments

- Inspired by [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io)
- Built with the [Model Context Protocol](https://modelcontextprotocol.io/)
- Compatible with [Draw.io](https://www.drawio.com/)