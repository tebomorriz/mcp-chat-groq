from core.groq import Groq
from mcp_client import MCPClient
from core.tools import ToolManager


class Chat:
    def __init__(
        self,
        groq_service: Groq,
        clients: dict[str, MCPClient],
    ):
        self.groq_service = groq_service
        self.clients = clients
        self.messages: list[dict] = []

    async def _process_query(self, query: str):
        self.messages.append({
            "role": "user",
            "content": query,
        })

    async def run(self, query: str) -> str:
        await self._process_query(query)

        while True:
            tools = await ToolManager.get_all_tools(self.clients)

            response = self.groq_service.chat(
                messages=self.messages,
                tools=tools,
            )

            assistant_message = response.choices[0].message

            self.groq_service.add_assistant_message(
                self.messages,
                response,
            )

            if response.choices[0].finish_reason == "tool_calls":
                tool_results = await ToolManager.execute_tool_requests(
                    self.clients,
                    assistant_message,
                )

                self.messages.extend(tool_results)

            else:
                return self.groq_service.text_from_message(response)
