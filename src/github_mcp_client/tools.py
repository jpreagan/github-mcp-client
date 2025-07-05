import json
import logging
from typing import Any

from mcp import types as mcp_types
from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_tool_message_param import ChatCompletionToolMessageParam

from .server import Server


def mcp_tool_to_openai_schema(tool: mcp_types.Tool) -> ChatCompletionToolParam:
    """Convert MCP tool to OpenAI function schema."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


async def execute_tool(server: Server, name: str, args: dict[str, Any]) -> Any:
    """Execute a tool and return its result."""
    result = await server.session.call_tool(name, args)
    
    if result.isError:
        error_content = result.structuredContent or [
            c.model_dump() for c in result.content
        ]
        raise RuntimeError(
            f"Tool '{name}' failed: {json.dumps(error_content)}"
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


async def handle_tool_calls(
    server: Server, 
    tool_calls: list[ChatCompletionMessageToolCall]
) -> list[ChatCompletionToolMessageParam]:
    """Handle multiple tool calls and return results."""
    results: list[ChatCompletionToolMessageParam] = []
    
    for call in tool_calls:
        name = call.function.name
        args = json.loads(call.function.arguments or "{}")
        
        print(f"🔧 Calling tool: {name} with params: {json.dumps(args)}")
        
        try:
            result = await execute_tool(server, name, args)
            print(f"✅ Tool '{name}' executed successfully")
        except Exception as exc:
            logging.error("Tool failed: %s", exc)
            result = {"error": str(exc)}
        
        results.append(ChatCompletionToolMessageParam(
            role="tool",
            tool_call_id=call.id,
            content=json.dumps(result, default=str),
        ))
    
    return results