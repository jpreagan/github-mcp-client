import asyncio
import json
import logging
import os
import shutil
from contextlib import AsyncExitStack
from dataclasses import asdict, is_dataclass
from typing import Any

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Configuration:
    def __init__(self) -> None:
        load_dotenv()
        self.api_key = os.getenv("LLM_API_KEY")

    @property
    def llm_api_key(self) -> str:
        if not self.api_key:
            raise ValueError("LLM_API_KEY not found in environment variables")
        return self.api_key


def tool_result_to_json(obj: Any) -> str:
    """Return a JSON string suitable for the `content` field of a tool message."""
    if isinstance(obj, BaseModel):
        return obj.model_dump_json()
    if is_dataclass(obj):
        return json.dumps(asdict(obj))
    return json.dumps(obj, default=str)


class Tool:
    def __init__(
        self, name: str, description: str, input_schema: dict[str, Any]
    ) -> None:
        self.name, self.description, self.input_schema = name, description, input_schema

    def to_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


class Server:
    def __init__(self, name: str, cfg: dict[str, Any]) -> None:
        self.name, self.cfg = name, cfg
        self.session: ClientSession | None = None
        self.stack = AsyncExitStack()

    async def initialize(self) -> None:
        cmd = shutil.which(self.cfg["command"])
        if cmd is None:
            raise ValueError(f"Command not found: {self.cfg['command']}")
        params = StdioServerParameters(
            command=cmd,
            args=self.cfg["args"],
            env={**os.environ, **self.cfg.get("env", {})},
        )
        read, write = await self.stack.enter_async_context(stdio_client(params))
        self.session = await self.stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

    async def list_tools(self) -> list["Tool"]:
        if not self.session:
            raise RuntimeError("Server not initialised")
        resp = await self.session.list_tools()
        tools: list[Tool] = []
        for item in resp:
            if isinstance(item, tuple) and item[0] == "tools":
                tools.extend(
                    Tool(t.name, t.description, t.inputSchema) for t in item[1]
                )
        return tools

    async def execute_tool(self, name: str, args: dict[str, Any]) -> Any:
        if not self.session:
            raise RuntimeError("Server not initialised")
        return await self.session.call_tool(name, args)

    async def close(self) -> None:
        await self.stack.aclose()


class LLMClient:
    def __init__(self, api_key: str, endpoint: str, model: str) -> None:
        self.oai = OpenAI(api_key=api_key, base_url=endpoint)
        self.model = model

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        resp = self.oai.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=4096,
        )
        return resp.choices[0].message.to_dict()


class ChatSession:
    def __init__(self, server: Server, llm: LLMClient) -> None:
        self.server, self.llm = server, llm

    async def run(self) -> None:
        await self.server.initialize()
        tools = await self.server.list_tools()
        logging.info(f"Found {len(tools)} available tools from MCP server")
        for tool in tools:
            logging.debug(f"  - {tool.name}")
        schemas = [t.to_schema() for t in tools]

        msgs = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to GitHub tools. "
                    "Choose the appropriate tool based on the user's question. "
                    "If no tool is needed reply directly."
                ),
            }
        ]

        while True:
            try:
                user = input(">>> ").strip()
                if not user:
                    continue
            except EOFError:
                break
            except KeyboardInterrupt:
                break

            msgs.append({"role": "user", "content": user})

            assistant = self.llm.chat(msgs, schemas)
            msgs.append(assistant)

            if assistant.get("tool_calls"):
                for call in assistant["tool_calls"]:
                    name = call["function"]["name"]
                    args = json.loads(call["function"]["arguments"])
                    logging.info(
                        (f"🔧 Calling tool: {name} with params: {json.dumps(args)}")
                    )
                    result = await self.server.execute_tool(name, args)
                    logging.info(f"✅ Tool '{name}' executed successfully")
                    msgs.append(
                        {
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "name": name,
                            "content": tool_result_to_json(result),
                        }
                    )
                assistant = self.llm.chat(msgs, schemas)
                msgs.append(assistant)

            print(f"{assistant['content'].strip()}\n")

        await self.server.close()


async def main() -> None:
    cfg = Configuration()
    github_cfg = {
        "command": "docker",
        "args": [
            "run",
            "-i",
            "--rm",
            "-e",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            "-e",
            "GITHUB_TOOLSETS=all",
            "ghcr.io/github/github-mcp-server",
        ],
        "env": {},
    }
    server = Server("github", github_cfg)
    llm = LLMClient(
        api_key=cfg.llm_api_key,
        endpoint="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
    )
    chat = ChatSession(server, llm)
    await chat.run()


if __name__ == "__main__":
    asyncio.run(main())
