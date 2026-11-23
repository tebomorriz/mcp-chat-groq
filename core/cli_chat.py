
from typing import List, Tuple
from mcp.types import Prompt, PromptMessage

from core.chat import Chat
from core.groq import Groq
from mcp_client import MCPClient


class CliChat(Chat):
    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        groq_service: Groq,
    ):
        super().__init__(
            clients=clients,
            groq_service=groq_service,
        )

        self.doc_client: MCPClient = doc_client

    async def list_prompts(self) -> list[Prompt]:
        return await self.doc_client.list_prompts()

    async def list_docs_ids(self) -> list[str]:
        return await self.doc_client.read_resource("docs://documents")

    async def get_doc_content(self, doc_id: str) -> str:
        return await self.doc_client.read_resource(
            f"docs://documents/{doc_id}"
        )

    async def get_prompt(
        self, command: str, doc_id: str
    ) -> list[PromptMessage]:
        return await self.doc_client.get_prompt(
            command,
            {"doc_id": doc_id},
        )

    async def _extract_resources(self, query: str) -> str:
        mentions = [
            word[1:]
            for word in query.split()
            if word.startswith("@")
        ]

        doc_ids = await self.list_docs_ids()
        mentioned_docs: list[Tuple[str, str]] = []

        for doc_id in doc_ids:
            if doc_id in mentions:
                content = await self.get_doc_content(doc_id)
                mentioned_docs.append((doc_id, content))

        return "".join(
            f'\n<document id="{doc_id}">\n{content}\n</document>\n'
            for doc_id, content in mentioned_docs
        )

    async def _process_command(self, query: str) -> bool:
        if not query.startswith("/"):
            return False

        words = query.split()

        if len(words) < 2:
            print("Please provide a document ID. Example: /format report.pdf")
            return True

        command = words[0][1:]
        doc_id = words[1]

        messages = await self.doc_client.get_prompt(
            command,
            {"doc_id": doc_id},
        )

        self.messages.extend(
            convert_prompt_messages_to_message_params(messages)
        )

        return True

    async def _process_query(self, query: str):
        if await self._process_command(query):
            return

        added_resources = await self._extract_resources(query)

        prompt = f"""
The user has a question:

<query>
{query}
</query>

The following context may be useful in answering their question:

<context>
{added_resources}
</context>

The user may reference documents using names like "@report.pdf".
If document content is included in the context, do not call an
additional tool to read that document.

Answer the user's question directly and concisely.
Start with the exact information they need.
Use the provided context without mentioning it.
"""

        self.messages.append({
            "role": "user",
            "content": prompt,
        })


def convert_prompt_message_to_message_param(
    prompt_message: PromptMessage,
) -> dict:
    role = (
        "user"
        if str(prompt_message.role).lower() == "user"
        else "assistant"
    )

    content = prompt_message.content

    if isinstance(content, dict):
        if content.get("type") == "text":
            return {
                "role": role,
                "content": content.get("text", ""),
            }

    elif hasattr(content, "text"):
        return {
            "role": role,
            "content": content.text,
        }

    elif isinstance(content, list):
        text_blocks = []

        for item in content:
            if isinstance(item, dict):
                item_type = item.get("type")
                item_text = item.get("text", "")
            else:
                item_type = getattr(item, "type", None)
                item_text = getattr(item, "text", "")

            if item_type == "text":
                text_blocks.append(item_text)

        return {
            "role": role,
            "content": "\n".join(text_blocks),
        }

    return {
        "role": role,
        "content": str(content) if isinstance(content, str) else "",
    }


def convert_prompt_messages_to_message_params(
    prompt_messages: List[PromptMessage],
) -> List[dict]:
    return [
        convert_prompt_message_to_message_param(msg)
        for msg in prompt_messages
    ]
