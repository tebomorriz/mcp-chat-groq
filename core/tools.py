import json
from typing import Optional
from mcp.types import CallToolResult, TextContent
from mcp_client import MCPClient


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[dict]:
        """Discover MCP tools and convert them to Groq function definitions."""
        tools = []

        for client in clients.values():
            tool_models = await client.list_tools()

            for tool in tool_models:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema,
                    },
                })

        return tools

    @classmethod
    async def _find_client_with_tool(
        cls,
        clients: list[MCPClient],
        tool_name: str,
    ) -> Optional[MCPClient]:
        """Find the MCP client that provides the requested tool."""
        for client in clients:
            tools = await client.list_tools()

            if any(tool.name == tool_name for tool in tools):
                return client

        return None

    @classmethod
    async def execute_tool_requests(
        cls,
        clients: dict[str, MCPClient],
        message,
    ) -> list[dict]:
        """Execute Groq tool calls through the relevant MCP clients."""
        tool_calls = message.tool_calls or []
        results = []

        for tool_call in tool_calls:
            tool_call_id = tool_call.id
            tool_name = tool_call.function.name

            try:
                tool_input = json.loads(tool_call.function.arguments)

                client = await cls._find_client_with_tool(
                    list(clients.values()),
                    tool_name,
                )

                if not client:
                    raise ValueError(
                        f"Could not find an MCP tool named '{tool_name}'"
                    )

                tool_output: CallToolResult = await client.call_tool(
                    tool_name,
                    tool_input,
                )

                content_list = [
                    item.text
                    for item in (tool_output.content or [])
                    if isinstance(item, TextContent)
                ]

                result_content = json.dumps(content_list)

                if tool_output.isError:
                    result_content = json.dumps({
                        "error": result_content
                    })

            except Exception as e:
                result_content = json.dumps({
                    "error": f"Error executing tool '{tool_name}': {e}"
                })

            results.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result_content,
            })

        return results
