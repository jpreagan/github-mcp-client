import os
from contextlib import AsyncExitStack
from types import TracebackType
from typing import Optional, Type

from mcp import types as mcp_types
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .config import Config


class Server:
    """MCP server lifecycle management."""

    def __init__(self, config: Config):
        self._config = config
        self._stack = AsyncExitStack()
        self._session: ClientSession | None = None

    async def __aenter__(self) -> "Server":
        params = StdioServerParameters(
            command="docker",
            args=[
                "run",
                "-i",
                "--rm",
                "-e",
                "GITHUB_PERSONAL_ACCESS_TOKEN",
                "ghcr.io/github/github-mcp-server",
            ],
            env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": self._config.github_token},
        )
        read, write = await self._stack.enter_async_context(stdio_client(params))
        self._session = await self._stack.enter_async_context(ClientSession(read, write))
        await self._session.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self._stack.aclose()

    @property
    def session(self) -> ClientSession:
        """The active MCP client session."""
        if self._session is None:
            raise RuntimeError("Server not started")
        return self._session

    async def list_tools(self) -> list[mcp_types.Tool]:
        """List available tools."""
        result = await self.session.list_tools()
        return result.tools