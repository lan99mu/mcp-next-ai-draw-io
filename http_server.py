"""
HTTP Server for real-time diagram preview

Provides a local HTTP server that serves the draw.io UI and manages
diagram state for real-time browser updates.
"""

import asyncio
import json
import socket
from typing import Optional, Dict, Any
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading

# State storage
_diagram_state: Dict[str, Dict[str, Any]] = {}
_server_port: Optional[int] = None
_server_thread: Optional[threading.Thread] = None


class DiagramRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for diagram serving"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if parsed.path == '/':
            # Serve the main HTML page
            session_id = params.get('mcp', [''])[0]
            html = self._get_html_page(session_id)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(html)))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        
        elif parsed.path == '/api/state':
            # Get current diagram state
            session_id = params.get('session', [''])[0]
            state = get_state(session_id)
            
            response = json.dumps(state or {})
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/state':
            # Update diagram state from browser
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
                session_id = data.get('session')
                xml = data.get('xml')
                svg = data.get('svg', '')
                
                if session_id and xml:
                    set_state(session_id, xml, svg)
                    
                    response = json.dumps({'status': 'ok'})
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(response)))
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                else:
                    self.send_error(400, 'Missing session or xml')
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def _get_html_page(self, session_id: str) -> str:
        """Generate HTML page with embedded draw.io"""
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MCP Draw.io - Real-time Preview</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            overflow: hidden;
        }}
        #container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        #header {{
            background: #2563eb;
            color: white;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        #header h1 {{
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }}
        #status {{
            font-size: 12px;
            opacity: 0.9;
        }}
        #iframe-container {{
            flex: 1;
            position: relative;
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="header">
            <h1>🎨 MCP Draw.io - Real-time Preview</h1>
            <div id="status">Connected - Session: {session_id[:8]}...</div>
        </div>
        <div id="iframe-container">
            <iframe id="drawio" src="https://embed.diagrams.net/?embed=1&ui=kennedy&spin=1&proto=json&saveAndExit=0"></iframe>
        </div>
    </div>
    
    <script>
        const sessionId = '{session_id}';
        let iframe;
        let lastXml = '';
        
        window.addEventListener('load', function() {{
            iframe = document.getElementById('drawio');
            
            // Listen for messages from draw.io
            window.addEventListener('message', function(evt) {{
                if (evt.data.length > 0) {{
                    try {{
                        const msg = JSON.parse(evt.data);
                        handleDrawioMessage(msg);
                    }} catch(e) {{
                        console.error('Error parsing message:', e);
                    }}
                }}
            }});
            
            // Poll for state updates from server
            setInterval(pollState, 1000);
        }});
        
        function handleDrawioMessage(msg) {{
            if (msg.event === 'init') {{
                // Draw.io is ready
                console.log('Draw.io initialized');
                pollState(); // Load initial state
            }} else if (msg.event === 'export') {{
                // Diagram was exported, save to server
                if (msg.format === 'xml') {{
                    saveState(msg.xml);
                }}
            }} else if (msg.event === 'save') {{
                // Auto-save
                iframe.contentWindow.postMessage(JSON.stringify({{
                    action: 'export',
                    format: 'xml'
                }}), '*');
            }}
        }}
        
        async function pollState() {{
            try {{
                const response = await fetch(`/api/state?session=${{sessionId}}`);
                const data = await response.json();
                
                if (data.xml && data.xml !== lastXml) {{
                    lastXml = data.xml;
                    
                    // Load the diagram into draw.io
                    iframe.contentWindow.postMessage(JSON.stringify({{
                        action: 'load',
                        xml: data.xml,
                        autosave: 1
                    }}), '*');
                }}
            }} catch(e) {{
                console.error('Error polling state:', e);
            }}
        }}
        
        async function saveState(xml) {{
            try {{
                await fetch('/api/state', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        session: sessionId,
                        xml: xml
                    }})
                }});
                lastXml = xml;
            }} catch(e) {{
                console.error('Error saving state:', e);
            }}
        }}
    </script>
</body>
</html>'''


def find_available_port(start_port: int, max_attempts: int = 20) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find available port in range {start_port}-{start_port + max_attempts}")


def start_http_server(preferred_port: int = 6002) -> int:
    """Start the HTTP server in a background thread"""
    global _server_port, _server_thread
    
    if _server_port is not None:
        return _server_port
    
    port = find_available_port(preferred_port)
    
    def run_server():
        server = HTTPServer(('localhost', port), DiagramRequestHandler)
        server.serve_forever()
    
    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()
    _server_port = port
    
    return port


def get_state(session_id: str) -> Optional[Dict[str, Any]]:
    """Get diagram state for a session"""
    return _diagram_state.get(session_id)


def set_state(session_id: str, xml: str, svg: str = ''):
    """Set diagram state for a session"""
    _diagram_state[session_id] = {
        'xml': xml,
        'svg': svg,
        'timestamp': asyncio.get_event_loop().time() if asyncio._get_running_loop() else 0
    }


def clear_state(session_id: str):
    """Clear diagram state for a session"""
    if session_id in _diagram_state:
        del _diagram_state[session_id]
