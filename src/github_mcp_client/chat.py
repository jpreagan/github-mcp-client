from typing import List, cast

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from .config import Config
from .server import Server
from .tools import handle_tool_calls, mcp_tool_to_openai_schema


def get_provider_name(base_url: str | None) -> str:
    """Extract clean provider name from base URL."""
    if not base_url:
        return "openai.com"

    domain = base_url.split("//")[1].split("/")[0]

    if domain.startswith("api."):
        domain = domain[4:]

    return domain


def show_welcome(config: Config) -> None:
    """Show welcome message with status."""
    provider = get_provider_name(config.openai_base_url)
    print(f"Using {config.model} via {provider}")
    print()


async def chat_loop(config: Config) -> None:
    """Main chat loop."""
    client = OpenAI(
        api_key=config.openai_api_key,
        base_url=config.openai_base_url,
    )

    async with Server(config) as server:
        show_welcome(config)

        tools = await server.list_tools()
        tool_schemas = [mcp_tool_to_openai_schema(t) for t in tools]

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
                user_input = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                return

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Goodbye!")
                return

            messages.append(
                ChatCompletionUserMessageParam(role="user", content=user_input)
            )

            while True:
                response = client.chat.completions.create(
                    model=config.model,
                    messages=messages,
                    tools=tool_schemas,
                )
                assistant = response.choices[0].message

                messages.append(cast(ChatCompletionMessageParam, assistant.to_dict()))

                if assistant.tool_calls:
                    tool_results = await handle_tool_calls(server, assistant.tool_calls)
                    messages.extend(tool_results)
                    continue

                if assistant.content:
                    print(assistant.content.strip(), end="\n\n")
                break
