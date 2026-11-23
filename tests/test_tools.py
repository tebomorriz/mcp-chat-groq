
import json
import pytest

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from mcp.types import TextContent
from core.tools import ToolManager


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_get_all_tools():
    """Verify MCP tools are converted to Groq function definitions."""
    mock_tool = SimpleNamespace(
        name="read_doc_contents",
        description="Read a document",
        inputSchema={"type": "object", "properties": {}},
    )

    client = Mock()
    client.list_tools = AsyncMock(return_value=[mock_tool])

    result = await ToolManager.get_all_tools({"server": client})

    assert len(result) == 1
    assert result[0]["type"] == "function"
    assert result[0]["function"]["name"] == "read_doc_contents"
    assert result[0]["function"]["description"] == "Read a document"
    assert result[0]["function"]["parameters"] == mock_tool.inputSchema


@pytest.mark.anyio
async def test_find_client_with_tool():
    """Verify the correct MCP client is found."""
    mock_tool = SimpleNamespace(name="read_doc_contents")

    client = Mock()
    client.list_tools = AsyncMock(return_value=[mock_tool])

    result = await ToolManager._find_client_with_tool(
        [client],
        "read_doc_contents",
    )

    assert result is client


@pytest.mark.anyio
async def test_find_client_with_missing_tool():
    """Verify None is returned when a tool cannot be found."""
    client = Mock()
    client.list_tools = AsyncMock(return_value=[])

    result = await ToolManager._find_client_with_tool(
        [client],
        "missing_tool",
    )

    assert result is None


@pytest.mark.anyio
async def test_execute_tool_request():
    """Verify an MCP tool call is executed and its result returned."""
    mock_tool = SimpleNamespace(name="read_doc_contents")

    client = Mock()
    client.list_tools = AsyncMock(return_value=[mock_tool])

    client.call_tool = AsyncMock(
        return_value=SimpleNamespace(
            content=[
                TextContent(type="text", text="Document contents here")
            ],
            isError=False,
        )
    )

    message = SimpleNamespace(
        tool_calls=[
            SimpleNamespace(
                id="call_123",
                function=SimpleNamespace(
                    name="read_doc_contents",
                    arguments='{"doc_id": "report.pdf"}',
                ),
            )
        ]
    )

    result = await ToolManager.execute_tool_requests(
        {"server": client},
        message,
    )

    assert len(result) == 1
    assert result[0]["role"] == "tool"
    assert result[0]["tool_call_id"] == "call_123"
    assert json.loads(result[0]["content"]) == [
        "Document contents here"
    ]

    client.call_tool.assert_called_once_with(
        "read_doc_contents",
        {"doc_id": "report.pdf"},
    )


@pytest.mark.anyio
async def test_execute_missing_tool():
    """Verify missing tools produce a structured error response."""
    client = Mock()
    client.list_tools = AsyncMock(return_value=[])

    message = SimpleNamespace(
        tool_calls=[
            SimpleNamespace(
                id="call_456",
                function=SimpleNamespace(
                    name="missing_tool",
                    arguments="{}",
                ),
            )
        ]
    )

    result = await ToolManager.execute_tool_requests(
        {"server": client},
        message,
    )

    assert len(result) == 1
    assert result[0]["tool_call_id"] == "call_456"

    error = json.loads(result[0]["content"])
    assert "error" in error
    assert "missing_tool" in error["error"]
