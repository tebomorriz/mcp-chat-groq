
import json

from mcp_server import docs, list_docs, get_doc, format, summarize


def test_list_documents():
    """Verify that the document resource lists all documents."""
    result = json.loads(list_docs())

    assert set(result) == set(docs.keys())


def test_get_document():
    """Verify that a document resource returns the correct content."""
    result = get_doc("report.pdf")

    assert result == docs["report.pdf"]


def test_format_prompt():
    """Verify that the format prompt includes document content."""
    result = format("deposition.md")

    assert "professional Markdown" in result
    assert docs["deposition.md"] in result


def test_summarize_prompt():
    """Verify that the summarize prompt includes document content."""
    result = summarize("financials.docx")

    assert "concise summary" in result
    assert docs["financials.docx"] in result
