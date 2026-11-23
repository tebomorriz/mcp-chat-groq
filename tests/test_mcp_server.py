
import pytest

from mcp_server import docs, read_doc_contents, edit_doc_contents


def test_read_existing_document():
    """Verify that an existing document can be read."""
    result = read_doc_contents("report.pdf")

    assert result == "The report details the state of a 20m condenser tower."


def test_read_nonexistent_document():
    """Verify that reading a missing document raises an error."""
    with pytest.raises(ValueError, match="not found"):
        read_doc_contents("missing.pdf")


def test_edit_existing_document():
    """Verify that an existing document can be updated."""
    doc_id = "plan.md"
    original_content = docs[doc_id]

    try:
        new_content = "Updated project implementation plan."

        result = edit_doc_contents(doc_id, new_content)

        assert result == f"Successfully updated '{doc_id}'."
        assert docs[doc_id] == new_content

    finally:
        docs[doc_id] = original_content


def test_edit_nonexistent_document():
    """Verify that editing a missing document raises an error."""
    with pytest.raises(ValueError, match="not found"):
        edit_doc_contents("missing.pdf", "New content")
