# MCP Chat — Groq-Powered AI Assistant

MCP Chat is an interactive command-line AI assistant powered by Groq and built using the Model Context Protocol (MCP).

The application demonstrates how an AI model can interact with external tools, access contextual resources, and execute reusable prompts through an MCP client-server architecture.

It currently includes a document management MCP server that allows the AI assistant to read and edit documents, retrieve document resources, and execute document-processing prompts.

## Features

- **AI conversations:** Interactive conversations powered by Groq.
- **MCP tool integration:** Discover and execute tools exposed by MCP servers.
- **Document retrieval:** Retrieve document contents using `@document_id` references.
- **Document editing:** Read and update documents through MCP tools.
- **MCP resources:** List available documents and retrieve their contents.
- **MCP prompts:** Execute reusable `/format` and `/summarize` commands.
- **CLI autocomplete:** Tab-based command autocomplete.
- **Extensible architecture:** Connect additional MCP servers.

## Technology Stack

| Technology             | Purpose                               |
| ---------------------- | ------------------------------------- |
| Python                 | Application development               |
| Groq API               | AI inference                          |
| OpenAI Python SDK      | Groq API integration                  |
| Model Context Protocol | AI-to-tool communication              |
| FastMCP                | MCP server implementation             |
| prompt-toolkit         | Interactive CLI and autocomplete      |
| python-dotenv          | Environment configuration             |
| uv                     | Dependency and environment management |

## Architecture

The application uses an MCP client-server architecture.

1. The CLI receives user input.
2. The chat component processes the request.
3. The Groq integration sends the conversation and available tool definitions to the model.
4. When a tool is requested, the tool manager routes the request to the appropriate MCP server.
5. The MCP server executes the operation and returns the result.
6. The result is passed back to Groq to generate the final response.

### Project Structure

```text
cli_project/
│
├── core/
│   ├── groq.py          # Groq API integration
│   ├── chat.py          # Conversation and tool orchestration
│   ├── cli.py           # Interactive CLI
│   ├── cli_chat.py      # CLI-specific chat functionality
│   └── tools.py         # MCP tool discovery and execution
│
├── mcp_server.py        # Document management MCP server
├── mcp_client.py        # MCP client implementation
├── main.py              # Application entry point
├── .env                 # Environment variables (not committed)
├── pyproject.toml       # Project dependencies and configuration
├── uv.lock              # Dependency lockfile
└── README.md
```

## Prerequisites

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/)
- A Groq API key from [Groq Console](https://console.groq.com/)

## Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd cli_project
```

### 2. Install dependencies

Using uv:

```bash
uv sync
```

Alternatively, activate your existing virtual environment and install the dependencies:

```bash
pip install -e .
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
USE_UV=1
```

Replace `your_groq_api_key` with your actual Groq API key.

**Security:** Never commit your `.env` file or expose your API key in source code, screenshots, or public repositories.

### 4. Run the application

With uv:

```bash
uv run main.py
```

Or, with an activated virtual environment:

```bash
python main.py
```

## Usage

### 1. Basic AI Conversation

Enter a message and press Enter:

```text
> Hello! Introduce yourself.
```

### 2. Document Retrieval Using @ References

Use `@` followed by a document ID to include its contents in your request:

```text
> What does @report.pdf contain?
```

### 3. MCP Tool Execution

Ask the assistant to use an available tool:

```text
> Use the read_doc_contents tool to retrieve financials.docx.
```

To edit a document:

```text
> Use the edit_doc_contents tool to update plan.md with the new project implementation plan.
```

### 4. MCP Prompts

Format a document:

```text
> /format deposition.md
```

Summarize a document:

```text
> /summarize financials.docx
```

Use the Tab key to autocomplete available commands.

## Available MCP Capabilities

### Tools

| Tool                | Description                                    |
| ------------------- | ---------------------------------------------- |
| `read_doc_contents` | Reads the contents of an existing document.    |
| `edit_doc_contents` | Replaces the contents of an existing document. |

### Resources

| Resource URI                | Description                    |
| --------------------------- | ------------------------------ |
| `docs://documents`          | Lists available document IDs.  |
| `docs://documents/{doc_id}` | Retrieves a specific document. |

### Prompts

| Prompt      | Description                                          |
| ----------- | ---------------------------------------------------- |
| `format`    | Rewrites a document in clean, professional Markdown. |
| `summarize` | Generates a concise document summary.                |

## Development and Extensibility

### Adding Documents

Add new documents to the `docs` dictionary in `mcp_server.py`.

### Adding MCP Tools

Implement additional functions using the FastMCP tool decorator:

```python
@mcp.tool()
def example_tool(input_text: str) -> str:
    """Example MCP tool."""
    return f"Processed: {input_text}"
```

The MCP client discovers available tools dynamically.

### Connecting Additional MCP Servers

The application supports additional MCP server scripts passed as command-line arguments:

```bash
python main.py path/to/another_server.py
```

## Important Implementation Note

The current document store uses an in-memory Python dictionary. Document edits remain available during the running server session but reset when the MCP server restarts.

A persistent database or file-backed document store would be a suitable future enhancement.

## Security Considerations

- Store API credentials in environment variables.
- Exclude `.env` from Git commits.
- Avoid exposing API keys in logs or error messages.
- Validate document identifiers and tool inputs.
- Apply appropriate permissions when connecting additional MCP servers.

## Future Improvements

- Persistent document storage.
- File-system-based document management.
- Support for additional MCP servers.
- Authentication and authorization.
- Automated tests for MCP tools and resources.
- Structured logging and error handling.

## License

Add your preferred open-source license before publishing this repository.
