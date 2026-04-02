"""Entry point for running the observability MCP server."""

import asyncio
import sys

from mcp_observability.server import main

if __name__ == "__main__":
    # Parse command-line arguments: python -m mcp_observability <victorialogs_url> <victoriatraces_url>
    victorialogs_url = sys.argv[1] if len(sys.argv) > 1 else None
    victoriatraces_url = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(main(victorialogs_url, victoriatraces_url))