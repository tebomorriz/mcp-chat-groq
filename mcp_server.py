
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


@mcp.tool()
def read_doc_contents(
    doc_id: str = Field(description="The ID of the document to read.")
) -> str:
    """Read the contents of a document."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found.")

    return docs[doc_id]


@mcp.tool()
def edit_doc_contents(
    doc_id: str = Field(description="The ID of the document to edit."),
    new_content: str = Field(description="The replacement document content."),
) -> str:
    """Replace the contents of an existing document."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found.")

    docs[doc_id] = new_content

    return f"Successfully updated '{doc_id}'."


@mcp.resource("docs://documents")
def list_docs() -> str:
    """List all available document IDs."""
    import json
    return json.dumps(list(docs.keys()))

@mcp.resource("docs://documents/{doc_id}")
def get_doc(doc_id: str) -> str:
    """Retrieve the contents of a specific document."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found.")

    return docs[doc_id]


@mcp.prompt()
def format(doc_id: str) -> str:
    """Rewrite a document in clean Markdown format."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found.")

    return f"""
Please rewrite the following document in clean, professional Markdown format.
Preserve all important information and improve its structure.

Document ID: {doc_id}

Document content:
{docs[doc_id]}
"""


@mcp.prompt()
def summarize(doc_id: str) -> str:
    """Summarize a document clearly and concisely."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found.")

    return f"""
Please provide a concise summary of this document.
Identify its main subject and key information.

Document ID: {doc_id}

Document content:
{docs[doc_id]}
"""


if __name__ == "__main__":
    mcp.run(transport="stdio")
