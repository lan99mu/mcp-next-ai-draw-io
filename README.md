# MCP Draw.io Server

一个基于 Python 的 Model Context Protocol (MCP) 服务器，使 AI 助手（如 GitHub Copilot）能够以编程方式生成 Draw.io 图表文件。该服务器提供创建图表、添加形状和连接的工具，生成的 .drawio 文件可以在 VS Code 的 Draw.io 扩展中打开和查看。

A Python-based Model Context Protocol (MCP) server that enables AI assistants (like GitHub Copilot) to generate Draw.io diagram files programmatically. This server provides tools for creating diagrams, adding shapes, and connecting them. The generated .drawio files can be opened and viewed in VS Code's Draw.io extension.

## Features

- ✍️ **Generate Draw.io XML files** - Create .drawio diagram files programmatically
- 🔷 **Multiple shape types** - Support for rectangle, ellipse, diamond, and more
- 🔗 **Connect shapes** - Add connections between shapes with customizable arrows
- 💾 **Standard Draw.io format** - Output compatible with Draw.io and diagrams.net
- 🤖 **MCP-compatible** - Works with VS Code Copilot and other MCP clients
- 📦 **Lightweight** - Simple Python implementation with minimal dependencies

**Note:** This server only generates Draw.io XML files. It does not include rendering capabilities. The generated files need to be opened in Draw.io (VS Code extension or web app) for visualization.

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

### `create_diagram`
Create a new Draw.io diagram.
- **Parameters:**
  - `name` (optional): Name of the diagram (default: "Untitled")

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

### `get_diagram`
Get the current diagram as Draw.io XML format.

### `list_shapes`
List all shapes currently in the diagram with their IDs and labels.

## Example Workflow

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
├── mcp_drawio_server.py    # Main MCP server implementation
├── pyproject.toml           # Project configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## How It Works

1. The MCP server runs as a background process
2. It communicates with MCP clients (like VS Code Copilot) via stdio
3. When prompted, the AI assistant calls the server's tools to:
   - Create diagram structures in memory
   - Add shapes and connections
   - Generate Draw.io-compatible XML
4. The generated XML can be saved to a `.drawio` file
5. Open the file in Draw.io (VS Code extension, desktop app, or web) to view and edit

**Important:** This server only **generates** Draw.io files. It does **not render** diagrams. You need Draw.io software to visualize the output.

## Supported Shape Types

- **rectangle**: Standard rectangular box
- **ellipse**: Circular/oval shape
- **diamond**: Diamond shape (often used for decision points)
- **parallelogram**: Parallelogram shape (often used for input/output)
- **hexagon**: Hexagon shape (often used for preparation steps)
- **cylinder**: Cylinder shape (often used for databases)
- **cloud**: Cloud shape (often used for cloud services)

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