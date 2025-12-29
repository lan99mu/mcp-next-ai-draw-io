#!/usr/bin/env python3
"""
Entry point for running mcp_drawio_server as a module.

This allows the server to be run with:
    python -m mcp_drawio_server
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())
