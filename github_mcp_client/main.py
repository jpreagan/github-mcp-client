import asyncio
import json
import logging
import os
import shutil
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Configuration:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("LLM_API_KEY")

    @property
    def llm_api_key(self):
        if not self.api_key:
            raise ValueError("LLM_API_KEY not found in environment variables")
        return self.api_key


def tool_result_to_json(obj):
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        try:
            if hasattr(obj, "__dict__"):
                return json.dumps(obj.__dict__, default=str)
            return json.dumps(str(obj))
        except (TypeError, ValueError):
            return json.dumps(str(obj))


class Tool:
    def __init__(self, name, description, input_schema):
        self.name = name
        self.description = description
        self.input_schema = input_schema

    def to_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


class Server:
    def __init__(self, name, cfg):
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

    async def execute_tool(self, name, args):
        if not self.session:
            raise RuntimeError("Server not initialised")
        return await self.session.call_tool(name, args)

    async def close(self):
        await self.stack.aclose()


class LLMClient:
    def __init__(self, api_key, endpoint, model):
        self.oai = OpenAI(api_key=api_key, base_url=endpoint)
        self.model = model

    def chat(self, messages, tools):
        resp = self.oai.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
        )
        return resp.choices[0].message.to_dict()


class ChatSession:
    def __init__(self, server, llm):
        self.server = server
        self.llm = llm

    async def run(self):
        await self.server.initialize()
        tools = await self.server.list_tools()
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

            while True:
                assistant = self.llm.chat(msgs, schemas)
                msgs.append(assistant)

                if assistant.get("tool_calls"):
                    for call in assistant["tool_calls"]:
                        name = call["function"]["name"]
                        args = json.loads(call["function"]["arguments"])
                        tool_payload_str = json.dumps(args)
                        logging.info(
                            f"🔧 Calling tool: {name} with params: {tool_payload_str}"
                        )
                        result = await self.server.execute_tool(name, args)
                        logging.info(f"✅ Tool '{name}' executed successfully")
                        tool_result_str = tool_result_to_json(result)
                        msgs.append(
                            {
                                "role": "tool",
                                "tool_call_id": call["id"],
                                "name": name,
                                "content": tool_result_str,
                            }
                        )
                    continue

                if "content" in assistant and assistant["content"]:
                    print(f"{assistant['content'].strip()}\n")
                    break

                break

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
            "GITHUB_DYNAMIC_TOOLSETS=1",
            "ghcr.io/github/github-mcp-server",
        ],
        "env": {},
    }
    server = Server("github", github_cfg)
    llm = LLMClient(
        api_key=cfg.llm_api_key,
        endpoint="https://api.together.xyz/v1",
        model="Qwen/Qwen2.5-72B-Instruct-Turbo",
    )
    chat = ChatSession(server, llm)
    await chat.run()


if __name__ == "__main__":
    asyncio.run(main())
