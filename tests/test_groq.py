
import pytest
from unittest.mock import Mock

from core.groq import Groq


@pytest.fixture(autouse=True)
def mock_groq_api_key(monkeypatch):
    """Provide a dummy API key for every test."""
    monkeypatch.setenv("GROQ_API_KEY", "test-api-key")


def test_groq_initialization():
    """Verify that the Groq adapter initializes correctly."""
    service = Groq(model="openai/gpt-oss-20b")

    assert service.model == "openai/gpt-oss-20b"
    assert service.client is not None


def test_text_from_message():
    """Verify that the adapter extracts assistant text."""
    service = Groq(model="openai/gpt-oss-20b")

    response = Mock()
    response.choices = [
        Mock(message=Mock(content="Hello from Groq!"))
    ]

    result = service.text_from_message(response)

    assert result == "Hello from Groq!"


def test_add_user_message():
    """Verify that user messages are added to conversation history."""
    service = Groq(model="openai/gpt-oss-20b")
    messages = []

    service.add_user_message(messages, "Hello!")

    assert messages == [
        {"role": "user", "content": "Hello!"}
    ]


def test_add_assistant_message():
    """Verify that assistant responses are added to conversation history."""
    service = Groq(model="openai/gpt-oss-20b")
    messages = []

    response = Mock()
    response.choices = [
        Mock(
            message=Mock(
                model_dump=lambda exclude_none: {
                    "role": "assistant",
                    "content": "Hello!"
                }
            )
        )
    ]

    service.add_assistant_message(messages, response)

    assert messages == [
        {"role": "assistant", "content": "Hello!"}
    ]
def test_chat_calls_groq_api():
    """Verify that chat sends the correct request to the Groq API."""
    service = Groq(model="openai/gpt-oss-20b")

    mock_response = Mock()
    service.client.chat.completions.create = Mock(
        return_value=mock_response
    )

    messages = [{"role": "user", "content": "Hello!"}]

    result = service.chat(messages)

    assert result == mock_response

    service.client.chat.completions.create.assert_called_once_with(
        model="openai/gpt-oss-20b",
        messages=messages,
        max_completion_tokens=4096,
        extra_body={"include_reasoning": False},
    )