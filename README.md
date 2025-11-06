# MCP Client

An intelligent MCP (Model Context Protocol) client that connects to MCP servers and uses Ollama for LLM-powered query processing with automatic tool calling.

## Features

- **MCP Server Integration**: Connects to MCP servers via stdio (supports both Python and JavaScript servers)
- **LLM-Powered Queries**: Uses Ollama for natural language processing and intelligent responses
- **Automatic Tool Calling**: Automatically converts MCP tools to Ollama function calling format and executes tool calls
- **Authentication Support**: Supports API key and Bearer token authentication
- **Interactive Chat Loop**: Provides an interactive command-line interface for querying
- **Environment-Based Configuration**: Uses `.env` files for secure credential management

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### Quick Install

```bash
pip install -e .
```

Or using `uv`:

```bash
uv pip install -e .
```

### Prerequisites

- Python >= 3.13
- Ollama installed and running (see [INSTALL_OLLAMA.md](INSTALL_OLLAMA.md))
- An MCP server to connect to (e.g., `my-first-mcp-server`)

## Configuration

### Environment Variables

Create a `.env` file in the client directory with the following optional variables:

```env
# Option 1: API Key Authentication
MCP_API_KEY=your-api-key-here

# Option 2: Bearer Token Authentication
MCP_TOKEN=your-bearer-token-here
# or
MCP_BEARER_TOKEN=your-bearer-token-here
```

**Note**: 
- If both API key and token are provided, API key takes precedence
- If neither is provided, the client will connect without authentication (requires server to have `MCP_AUTH_REQUIRED=false`)

### Example Configuration

To match the default server configuration:

```env
MCP_API_KEY=default-api-key-12345
```

## Usage

### Basic Usage

Run the client with the default server path:

```bash
python client.py
```

Or specify a custom server path:

```bash
python client.py path/to/server/main.py
```

### Programmatic Usage

```python
import asyncio
from client import MCPClient

async def main():
    # Create client with optional authentication
    client = MCPClient(
        model="llama3.2",  # Ollama model to use
        api_key="your-api-key",  # Optional: API key
        token="your-token"  # Optional: Bearer token
    )
    
    try:
        # Connect to server
        await client.connect_to_server("path/to/server/main.py")
        
        # Check authentication status
        if client.is_authenticated():
            print(f"Authenticated using: {client.get_auth_type()}")
        
        # Process queries
        response = await client.process_query("Check leave balance for E001")
        print(response)
        
        # Or run interactive chat loop
        await client.chat_loop()
        
    finally:
        await client.cleanup()

asyncio.run(main())
```

## How It Works

1. **Connection**: The client connects to an MCP server via stdio communication
2. **Tool Discovery**: Fetches available tools from the server
3. **Tool Conversion**: Converts MCP tools to OpenAI-compatible function calling format for Ollama
4. **Query Processing**: 
   - Sends user query to Ollama with available tools
   - Ollama intelligently decides when to call tools
   - Executes tool calls on the MCP server
   - Returns combined results to the user

## Example Session

```
Connecting to MCP server: ..\my-first-mcp-server\main.py
Using API key authentication
Initializing session...
Fetching available tools...
Session initialized successfully
Authentication verified (api_key)

Connected to server with tools: ['get_leave_balance', 'apply_leave', 'get_leave_history']

MCP Client Started!
Type your queries or 'quit' to exit.

Query: Check leave balance for employee E001

E001 has 18 leave days remaining.

Query: Apply for leave on 2025-04-15 for employee E001

Tool 'apply_leave' result: Leave applied for 1 day(s). Remaining balance: 17.

Query: quit
```

## API Reference

### MCPClient Class

#### `__init__(model="llama3.2", api_key=None, token=None)`

Initialize the MCP client.

- `model`: Ollama model name (default: "llama3.2")
- `api_key`: Optional API key for authentication
- `token`: Optional Bearer token for authentication

#### `async connect_to_server(server_script_path)`

Connect to an MCP server.

- `server_script_path`: Path to the server script (.py or .js)

#### `async process_query(query) -> str`

Process a query using Ollama and available tools.

- `query`: The user's query string
- Returns: The processed response

#### `async chat_loop()`

Run an interactive chat loop for continuous querying.

#### `is_authenticated() -> bool`

Check if authentication credentials are configured.

#### `get_auth_type() -> Optional[str]`

Get the type of authentication being used ("api_key", "bearer", or None).

#### `async cleanup()`

Clean up resources and close connections.

## Troubleshooting

### Authentication Errors

If you see authentication errors:
1. Ensure your `.env` file contains the correct credentials
2. Verify the server expects the same credentials (check server's `.env` file)
3. Check if the server has `MCP_AUTH_REQUIRED=true` set

### Connection Errors

- Ensure the server path is correct
- Verify the server script exists and is executable
- Check that the server dependencies are installed

### Ollama Errors

- Ensure Ollama is running: `ollama serve`
- Verify the model is installed: `ollama list`
- Install the model if needed: `ollama pull llama3.2`

## See Also

- [INSTALL.md](INSTALL.md) - Installation instructions
- [INSTALL_OLLAMA.md](INSTALL_OLLAMA.md) - Ollama setup guide
- [../my-first-mcp-server/README.md](../my-first-mcp-server/README.md) - Server documentation
