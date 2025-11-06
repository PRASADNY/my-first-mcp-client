import asyncio
import sys
import json
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import ollama

from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self, model: str = "llama3.2", api_key: Optional[str] = None, token: Optional[str] = None):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.model = model
        
        # Authentication credentials
        # Priority: explicit parameter > environment variable > None
        self.api_key = api_key or os.getenv("MCP_API_KEY")
        self.token = token or os.getenv("MCP_TOKEN") or os.getenv("MCP_BEARER_TOKEN")
        
        # If both API key and token are provided, API key takes precedence
        if self.api_key:
            self.auth_type = "api_key"
            self.auth_value = self.api_key
        elif self.token:
            self.auth_type = "bearer"
            self.auth_value = self.token
        else:
            self.auth_type = None
            self.auth_value = None
    # methods will go here

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        # Resolve the absolute path
        if not os.path.isabs(server_script_path):
            server_script_path = os.path.abspath(server_script_path)
        
        if not os.path.exists(server_script_path):
            raise FileNotFoundError(f"Server script not found: {server_script_path}")
        
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        # Prepare environment variables for the server process
        # Start with current environment and add authentication
        server_env = os.environ.copy()
        
        if self.auth_type == "api_key":
            server_env["MCP_API_KEY"] = self.auth_value
            print("Using API key authentication")
        elif self.auth_type == "bearer":
            server_env["MCP_TOKEN"] = self.auth_value
            server_env["MCP_BEARER_TOKEN"] = self.auth_value
            print("Using Bearer token authentication")
        else:
            print("No authentication configured - connecting without authentication")

        # Use sys.executable to ensure we use the same Python interpreter
        command = sys.executable if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=server_env
        )
        
        print(f"Connecting to MCP server: {server_script_path}")

        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            print("Initializing session...")
            await self.session.initialize()
            
            # Verify authentication by attempting to list tools
            # If authentication fails, the server should return an error
            print("Fetching available tools...")
            try:
                response = await self.session.list_tools()
                tools = response.tools
                print("Session initialized successfully")
                if self.auth_type:
                    print(f"Authentication verified ({self.auth_type})")
                print("\nConnected to server with tools:", [tool.name for tool in tools])
            except Exception as auth_error:
                if "auth" in str(auth_error).lower() or "unauthorized" in str(auth_error).lower():
                    raise RuntimeError(f"Authentication failed: {str(auth_error)}. Please check your credentials.")
                raise
        except Exception as e:
            print(f"Error connecting to server: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    async def process_query(self, query: str) -> str:
        """Process a query using Ollama and available tools"""
        if self.session is None:
            raise RuntimeError("Session is not initialized. Call connect_to_server() first.")

        # Get available tools from the server and convert to Ollama format
        response = await self.session.list_tools()
        available_tools = response.tools  # list of tool objects from the MCP server
        
        # Convert MCP tools to Ollama function calling format
        tools = []
        for tool in available_tools:
            tool_dict = tool.model_dump()
            # Convert to OpenAI-compatible format for Ollama
            function_def = {
                "type": "function",
                "function": {
                    "name": tool_dict.get("name", ""),
                    "description": tool_dict.get("description", ""),
                    "parameters": tool_dict.get("inputSchema", {})
                }
            }
            tools.append(function_def)

        # Call Ollama with tool/function calling support
        messages = [{"role": "user", "content": query}]
        
        # Use Ollama's chat API with tools
        response = await asyncio.to_thread(
            ollama.chat,
            model=self.model,
            messages=messages,
            tools=tools if tools else None
        )

        # Handle response
        message = response.get("message", {})
        content = message.get("content", "")
        
        # Check if tool calls were made
        tool_calls = message.get("tool_calls", [])
        if tool_calls:
            # Execute tool calls and get responses
            tool_responses = []
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                function_name = function.get("name", "")
                function_args_raw = function.get("arguments", {})
                
                # Parse arguments if it's a string
                if isinstance(function_args_raw, str):
                    try:
                        function_args = json.loads(function_args_raw)
                    except json.JSONDecodeError:
                        function_args = {}
                else:
                    function_args = function_args_raw if isinstance(function_args_raw, dict) else {}
                
                # Call the MCP tool
                try:
                    tool_result = await self.session.call_tool(function_name, arguments=function_args)
                    # Extract text content from tool result
                    if hasattr(tool_result, 'content'):
                        result_text = tool_result.content[0].text if (hasattr(tool_result.content, '__iter__') and len(tool_result.content) > 0) else str(tool_result.content)
                    else:
                        result_text = str(tool_result)
                    tool_responses.append(f"Tool '{function_name}' result: {result_text}")
                except Exception as e:
                    tool_responses.append(f"Error calling tool '{function_name}': {str(e)}")
            
            # Combine content and tool responses
            return "\n".join([content] + tool_responses) if content else "\n".join(tool_responses)
        
        return content if content else ""

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    def is_authenticated(self) -> bool:
        """Check if authentication credentials are configured"""
        return self.auth_type is not None
    
    def get_auth_type(self) -> Optional[str]:
        """Get the type of authentication being used"""
        return self.auth_type
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    # Use the server path from command line if provided, otherwise use default
    if len(sys.argv) >= 2:
        server_path = sys.argv[1]
    else:
        # Default path relative to client directory
        import os
        server_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'my-first-mcp-server', 'main.py')
        print(f"Using default server path: {server_path}")

    client = MCPClient()
    try:
        await client.connect_to_server(server_path)
        await client.chat_loop()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())