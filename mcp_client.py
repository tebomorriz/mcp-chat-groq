
import sys
import asyncio
import json
from typing import Optional, Any
from contextlib import AsyncExitStack

from pydantic import AnyUrl
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )

        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        _stdio, _write = stdio_transport

        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write)
        )

        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized. Call connect first."
            )

        return self._session

    async def list_tools(self) -> list[types.Tool]:
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(
        self,
        tool_name: str,
        tool_input: dict,
    ) -> types.CallToolResult:
        return await self.session().call_tool(
            tool_name,
            arguments=tool_input,
        )

    async def list_prompts(self) -> list[types.Prompt]:
        result = await self.session().list_prompts()
        return result.prompts

    async def get_prompt(
        self,
        prompt_name: str,
        args: dict[str, str],
    ):
        result = await self.session().get_prompt(
            prompt_name,
            arguments=args,
        )

        return result.messages

    async def read_resource(self, uri: str) -> Any:
        result = await self.session().read_resource(
            AnyUrl(uri)
        )

        contents = result.contents

        if not contents:
            return ""

        resource_content = contents[0]

        if hasattr(resource_content, "text"):
            content = resource_content.text
        elif hasattr(resource_content, "blob"):
            content = resource_content.blob.decode("utf-8")
        else:
            return ""

        if uri == "docs://documents":
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content

        return content

    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


async def main():
    async with MCPClient(
        command="uv",
        args=["run", "mcp_server.py"],
    ) as client:
        print("Connected to MCP server successfully.")

        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools])

        prompts = await client.list_prompts()
        print("Available prompts:", [prompt.name for prompt in prompts])


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )

    asyncio.run(main())
