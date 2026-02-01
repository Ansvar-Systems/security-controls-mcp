"""Entry point for the MCP server."""

import asyncio

from .server import main as async_main


def main():
    """Sync entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
