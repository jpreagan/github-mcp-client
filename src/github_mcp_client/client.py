from __future__ import annotations

import json
import logging
import os
import shutil
from contextlib import AsyncExitStack
from types import TracebackType
from typing import Any, List, Optional, Type, cast

from mcp import types as mcp_types
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)


def mcp_tool_to_openai_schema(
    tool: mcp_types.Tool,
) -> ChatCompletionToolParam:
    """Return the OpenAI function-calling schema for an MCP tool."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


class Server:
    """Thin async wrapper around a MCP stdio server."""

    def __init__(
        self, command: str, args: list[str], env: dict[str, str] | None = None
    ):
        self._cmd = shutil.which(command) or command
        self._args = args
        self._env = {**os.environ, **(env or {})}
        self._stack = AsyncExitStack()
        self._session: ClientSession | None = None

    async def __aenter__(self) -> "Server":
        params = StdioServerParameters(
            command=self._cmd,
            args=self._args,
            env=self._env,
        )
        read, write = await self._stack.enter_async_context(stdio_client(params))
        self._session = await self._stack.enter_async_context(
            ClientSession(read, write)
        )
        await self._session.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> bool | None:
        await self._stack.aclose()
        return None

    @property
    def session(self) -> ClientSession:
        """The active MCP client session."""
        if self._session is None:
            raise RuntimeError("Server not started. Use 'async with Server(...)'")
        return self._session

    async def list_tools(self) -> list[mcp_types.Tool]:
        """List the tools available on the server."""
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, name: str, args: dict[str, Any]) -> Any:
        """Call a tool on the server and return its result."""
        result = await self.session.call_tool(name, args)

        if result.isError:
            error_content = result.structuredContent or [
                c.model_dump() for c in result.content
            ]
            raise RuntimeError(
                f"Tool '{name}' failed with arguments {args}: {json.dumps(error_content)}"
            )

        if result.structuredContent is not None:
            return result.structuredContent

        text_parts = [
            block.text
            for block in result.content
            if isinstance(block, mcp_types.TextContent)
        ]
        if text_parts:
            return "\n".join(text_parts)

        return [block.model_dump() for block in result.content]


async def chat_loop(model: str = "gpt-4.1") -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in your environment")
    client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL"))

    async with Server(
        command="docker",
        args=[
            "run",
            "-i",
            "--rm",
            "-e",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            "ghcr.io/github/github-mcp-server",
        ],
    ) as server:
        tools = await server.list_tools()
        tool_schemas: list[ChatCompletionToolParam] = [
            mcp_tool_to_openai_schema(t) for t in tools
        ]

        messages: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(
                role="system",
                content=(
                    "You are a helpful assistant with access to GitHub tools. "
                    "Decide whether a user request needs a tool call; "
                    "if not, answer directly."
                ),
            )
        ]

        while True:
            try:
                user_in = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if not user_in:
                continue

            messages.append(
                ChatCompletionUserMessageParam(role="user", content=user_in)
            )

            while True:
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tool_schemas,
                )
                assistant = resp.choices[0].message

                messages.append(cast(ChatCompletionMessageParam, assistant.to_dict()))

                if assistant.tool_calls:
                    for call in assistant.tool_calls:
                        name = call.function.name
                        args = json.loads(call.function.arguments or "{}")

                        print(
                            f"🔧 Calling tool: {name} with params: {json.dumps(args)}"
                        )
                        try:
                            result = await server.call_tool(name, args)
                            print(f"✅ Tool '{name}' executed successfully")
                        except Exception as exc:
                            logging.error("Tool failed: %s", exc)
                            result = {"error": str(exc)}

                        messages.append(
                            ChatCompletionToolMessageParam(
                                role="tool",
                                tool_call_id=call.id,
                                content=json.dumps(result, default=str),
                            )
                        )
                    continue

                if assistant.content:
                    print(assistant.content.strip(), end="\n\n")
                break
