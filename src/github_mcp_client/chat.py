from typing import List, cast

from mcp import types as mcp_types
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
    print("Type /help for commands")
    print()


def _handle_tools_command(tools: List[mcp_types.Tool]) -> None:
    """Handle /tools command to show available tools."""
    if not tools:
        print("No tools available.\n")
        return

    print("Available tools:")
    for tool in tools:
        print(f"  • {tool.name}")
        if tool.description:
            print(f"    {tool.description}")
    print()


def _handle_help_command() -> None:
    """Handle /help command to show available commands."""
    print("Available commands:")
    print("  /tools  - List available tools")
    print("  /help   - Show this help message")
    print("  /exit   - Exit the chat")
    print()


def _handle_exit_command() -> bool:
    """Handle /exit command to exit the chat."""
    print("Goodbye!")
    return True


def handle_command(user_input: str, tools: List[mcp_types.Tool]) -> bool:
    """Handle REPL commands. Returns True if a command was handled."""
    if not user_input.startswith("/"):
        return False

    command = user_input.lower().strip()

    if command == "/tools":
        _handle_tools_command(tools)
        return True
    elif command == "/help":
        _handle_help_command()
        return True
    elif command == "/exit":
        return _handle_exit_command()
    else:
        print(f"Unknown command: {command}")
        print("Type /help for available commands.\n")
        return True


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

            if handle_command(user_input, tools):
                if user_input.lower().strip() == "/exit":
                    return
                continue

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
