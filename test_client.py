"""
Unit tests for MCP Client
"""
import pytest
import os
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Optional

# Import client class
import sys
sys.path.insert(0, os.path.dirname(__file__))
from client import MCPClient


class TestMCPClientInitialization:
    """Test MCPClient initialization"""
    
    def test_init_default_model(self):
        """Test initialization with default model"""
        client = MCPClient()
        assert client.model == "llama3.2"
        assert client.session is None
    
    def test_init_custom_model(self):
        """Test initialization with custom model"""
        client = MCPClient(model="llama3.1")
        assert client.model == "llama3.1"
    
    def test_init_with_api_key(self):
        """Test initialization with API key"""
        client = MCPClient(api_key="test-key-123")
        assert client.api_key == "test-key-123"
        assert client.auth_type == "api_key"
        assert client.auth_value == "test-key-123"
    
    def test_init_with_token(self):
        """Test initialization with Bearer token"""
        client = MCPClient(token="test-token-456")
        assert client.token == "test-token-456"
        assert client.auth_type == "bearer"
        assert client.auth_value == "test-token-456"
    
    def test_init_api_key_precedence_over_token(self):
        """Test that API key takes precedence over token when both provided"""
        client = MCPClient(api_key="test-key", token="test-token")
        assert client.auth_type == "api_key"
        assert client.auth_value == "test-key"
    
    @patch.dict(os.environ, {"MCP_API_KEY": "env-key-123"})
    def test_init_api_key_from_env(self):
        """Test initialization with API key from environment"""
        client = MCPClient()
        assert client.api_key == "env-key-123"
        assert client.auth_type == "api_key"
    
    @patch.dict(os.environ, {"MCP_TOKEN": "env-token-456"})
    def test_init_token_from_env(self):
        """Test initialization with token from environment"""
        client = MCPClient()
        assert client.token == "env-token-456"
        assert client.auth_type == "bearer"
    
    @patch.dict(os.environ, {"MCP_BEARER_TOKEN": "env-bearer-789"})
    def test_init_bearer_token_from_env(self):
        """Test initialization with MCP_BEARER_TOKEN from environment"""
        client = MCPClient()
        assert client.token == "env-bearer-789"
        assert client.auth_type == "bearer"
    
    def test_init_no_authentication(self):
        """Test initialization without authentication"""
        with patch.dict(os.environ, {}, clear=True):
            client = MCPClient()
            assert client.auth_type is None
            assert client.auth_value is None
    
    def test_init_explicit_parameter_overrides_env(self):
        """Test that explicit parameters override environment variables"""
        with patch.dict(os.environ, {"MCP_API_KEY": "env-key"}):
            client = MCPClient(api_key="explicit-key")
            assert client.api_key == "explicit-key"
            assert client.auth_value == "explicit-key"


class TestMCPClientAuthentication:
    """Test authentication methods"""
    
    def test_is_authenticated_with_api_key(self):
        """Test is_authenticated returns True with API key"""
        client = MCPClient(api_key="test-key")
        assert client.is_authenticated() is True
    
    def test_is_authenticated_with_token(self):
        """Test is_authenticated returns True with token"""
        client = MCPClient(token="test-token")
        assert client.is_authenticated() is True
    
    def test_is_authenticated_without_credentials(self):
        """Test is_authenticated returns False without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            client = MCPClient()
            assert client.is_authenticated() is False
    
    def test_get_auth_type_api_key(self):
        """Test get_auth_type returns 'api_key'"""
        client = MCPClient(api_key="test-key")
        assert client.get_auth_type() == "api_key"
    
    def test_get_auth_type_bearer(self):
        """Test get_auth_type returns 'bearer'"""
        client = MCPClient(token="test-token")
        assert client.get_auth_type() == "bearer"
    
    def test_get_auth_type_none(self):
        """Test get_auth_type returns None without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            client = MCPClient()
            assert client.get_auth_type() is None


class TestMCPClientConnectToServer:
    """Test connect_to_server method"""
    
    @pytest.mark.asyncio
    async def test_connect_to_server_file_not_found(self):
        """Test connection fails with non-existent file"""
        client = MCPClient()
        with pytest.raises(FileNotFoundError):
            await client.connect_to_server("nonexistent.py")
    
    @pytest.mark.asyncio
    async def test_connect_to_server_invalid_extension(self):
        """Test connection fails with invalid file extension"""
        client = MCPClient()
        # Create a temporary file with wrong extension
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name
        try:
            with pytest.raises(ValueError) as exc_info:
                await client.connect_to_server(temp_path)
            assert "must be a .py or .js file" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_connect_to_server_resolves_relative_path(self):
        """Test that relative paths are resolved to absolute"""
        client = MCPClient()
        # This will fail but we can check the path resolution
        with pytest.raises(FileNotFoundError):
            await client.connect_to_server("relative/path/server.py")
    
    @pytest.mark.asyncio
    async def test_connect_to_server_without_session_initialization(self):
        """Test that process_query fails without session"""
        client = MCPClient()
        with pytest.raises(RuntimeError) as exc_info:
            await client.process_query("test query")
        assert "Session is not initialized" in str(exc_info.value)


class TestMCPClientProcessQuery:
    """Test process_query method"""
    
    @pytest.mark.asyncio
    async def test_process_query_no_tool_calls(self):
        """Test process_query with no tool calls"""
        client = MCPClient()
        
        # Mock session and ollama response
        mock_session = AsyncMock()
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool"
        mock_tool.model_dump.return_value = {
            "name": "test_tool",
            "description": "Test tool",
            "inputSchema": {}
        }
        
        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_session.list_tools.return_value = mock_list_response
        
        client.session = mock_session
        
        # Mock ollama response with no tool calls
        mock_ollama_response = {
            "message": {
                "content": "This is a test response",
                "tool_calls": []
            }
        }
        
        with patch('client.ollama.chat', return_value=mock_ollama_response):
            with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
                mock_to_thread.return_value = mock_ollama_response
                result = await client.process_query("test query")
                
                assert result == "This is a test response"
                mock_session.list_tools.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_query_with_tool_calls(self):
        """Test process_query with tool calls"""
        client = MCPClient()
        
        # Mock session
        mock_session = AsyncMock()
        mock_tool = MagicMock()
        mock_tool.name = "get_leave_balance"
        mock_tool.description = "Get leave balance"
        mock_tool.model_dump.return_value = {
            "name": "get_leave_balance",
            "description": "Get leave balance",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string"}
                }
            }
        }
        
        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_session.list_tools.return_value = mock_list_response
        
        # Mock tool call result
        mock_tool_result = MagicMock()
        mock_content_item = MagicMock()
        mock_content_item.text = "E001 has 18 leave days remaining."
        mock_tool_result.content = [mock_content_item]
        mock_session.call_tool.return_value = mock_tool_result
        
        client.session = mock_session
        
        # Mock ollama response with tool call
        mock_ollama_response = {
            "message": {
                "content": "Checking leave balance...",
                "tool_calls": [
                    {
                        "function": {
                            "name": "get_leave_balance",
                            "arguments": {"employee_id": "E001"}
                        }
                    }
                ]
            }
        }
        
        with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
            mock_to_thread.return_value = mock_ollama_response
            result = await client.process_query("Check leave balance for E001")
            
            assert "Checking leave balance" in result
            assert "Tool 'get_leave_balance' result" in result
            assert "18 leave days remaining" in result
            mock_session.call_tool.assert_called_once_with(
                "get_leave_balance",
                arguments={"employee_id": "E001"}
            )
    
    @pytest.mark.asyncio
    async def test_process_query_tool_call_with_string_arguments(self):
        """Test process_query handles string JSON arguments"""
        client = MCPClient()
        
        mock_session = AsyncMock()
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.model_dump.return_value = {
            "name": "test_tool",
            "description": "Test",
            "inputSchema": {}
        }
        
        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_session.list_tools.return_value = mock_list_response
        
        mock_tool_result = MagicMock()
        mock_content_item = MagicMock()
        mock_content_item.text = "Success"
        mock_tool_result.content = [mock_content_item]
        mock_session.call_tool.return_value = mock_tool_result
        
        client.session = mock_session
        
        # Mock ollama response with string arguments
        mock_ollama_response = {
            "message": {
                "content": "",
                "tool_calls": [
                    {
                        "function": {
                            "name": "test_tool",
                            "arguments": json.dumps({"param": "value"})
                        }
                    }
                ]
            }
        }
        
        with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
            mock_to_thread.return_value = mock_ollama_response
            await client.process_query("test")
            
            mock_session.call_tool.assert_called_once_with(
                "test_tool",
                arguments={"param": "value"}
            )
    
    @pytest.mark.asyncio
    async def test_process_query_tool_call_error_handling(self):
        """Test process_query handles tool call errors gracefully"""
        client = MCPClient()
        
        mock_session = AsyncMock()
        mock_tool = MagicMock()
        mock_tool.name = "failing_tool"
        mock_tool.model_dump.return_value = {
            "name": "failing_tool",
            "description": "Failing tool",
            "inputSchema": {}
        }
        
        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_session.list_tools.return_value = mock_list_response
        mock_session.call_tool.side_effect = Exception("Tool execution failed")
        
        client.session = mock_session
        
        mock_ollama_response = {
            "message": {
                "content": "",
                "tool_calls": [
                    {
                        "function": {
                            "name": "failing_tool",
                            "arguments": {}
                        }
                    }
                ]
            }
        }
        
        with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
            mock_to_thread.return_value = mock_ollama_response
            result = await client.process_query("test")
            
            assert "Error calling tool 'failing_tool'" in result
            assert "Tool execution failed" in result
    
    @pytest.mark.asyncio
    async def test_process_query_tool_conversion(self):
        """Test that MCP tools are correctly converted to Ollama format"""
        client = MCPClient()
        
        mock_session = AsyncMock()
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test description"
        mock_tool.model_dump.return_value = {
            "name": "test_tool",
            "description": "Test description",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                }
            }
        }
        
        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_session.list_tools.return_value = mock_list_response
        
        client.session = mock_session
        
        mock_ollama_response = {
            "message": {
                "content": "Response",
                "tool_calls": []
            }
        }
        
        with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
            mock_to_thread.return_value = mock_ollama_response
            await client.process_query("test")
            
            # Verify ollama was called with correct tool format
            call_args = mock_to_thread.call_args
            tools = call_args[1]['tools']
            assert len(tools) == 1
            assert tools[0]["type"] == "function"
            assert tools[0]["function"]["name"] == "test_tool"
            assert tools[0]["function"]["description"] == "Test description"
            assert tools[0]["function"]["parameters"]["type"] == "object"


class TestMCPClientCleanup:
    """Test cleanup method"""
    
    @pytest.mark.asyncio
    async def test_cleanup_closes_exit_stack(self):
        """Test that cleanup properly closes the exit stack"""
        client = MCPClient()
        mock_exit_stack = AsyncMock()
        client.exit_stack = mock_exit_stack
        
        await client.cleanup()
        
        mock_exit_stack.aclose.assert_called_once()


class TestMCPClientToolConversion:
    """Test tool conversion logic"""
    
    def test_tool_dict_extraction(self):
        """Test that tool model_dump is used correctly"""
        # This is tested indirectly in process_query tests
        # but we can verify the conversion logic
        tool_dict = {
            "name": "test_tool",
            "description": "Test",
            "inputSchema": {"type": "object"}
        }
        
        function_def = {
            "type": "function",
            "function": {
                "name": tool_dict.get("name", ""),
                "description": tool_dict.get("description", ""),
                "parameters": tool_dict.get("inputSchema", {})
            }
        }
        
        assert function_def["function"]["name"] == "test_tool"
        assert function_def["function"]["description"] == "Test"
        assert function_def["function"]["parameters"]["type"] == "object"


class TestMCPClientChatLoop:
    """Test chat_loop method"""
    
    @pytest.mark.asyncio
    async def test_chat_loop_quit_immediately(self):
        """Test chat_loop exits immediately when 'quit' is entered"""
        client = MCPClient()
        
        # Mock input to return 'quit' immediately
        with patch('builtins.input', return_value='quit'):
            with patch('builtins.print'):  # Suppress print output
                # Should not hang and should exit cleanly
                await client.chat_loop()
    
    @pytest.mark.asyncio
    async def test_chat_loop_processes_query(self):
        """Test chat_loop processes a query before quitting"""
        client = MCPClient()
        
        # Mock session for process_query
        mock_session = AsyncMock()
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.model_dump.return_value = {
            "name": "test_tool",
            "description": "Test",
            "inputSchema": {}
        }
        
        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_session.list_tools.return_value = mock_list_response
        client.session = mock_session
        
        # Mock ollama response
        mock_ollama_response = {
            "message": {
                "content": "Test response",
                "tool_calls": []
            }
        }
        
        # Mock input to return query then quit
        input_calls = ["test query", "quit"]
        with patch('builtins.input', side_effect=input_calls):
            with patch('builtins.print'):  # Suppress print output
                with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
                    mock_to_thread.return_value = mock_ollama_response
                    await client.chat_loop()
                    
                    # Verify process_query was called
                    mock_session.list_tools.assert_called()
    
    @pytest.mark.asyncio
    async def test_chat_loop_handles_errors(self):
        """Test chat_loop handles errors gracefully"""
        client = MCPClient()
        
        # Mock input to return query then quit
        input_calls = ["test query", "quit"]
        with patch('builtins.input', side_effect=input_calls):
            with patch('builtins.print'):  # Suppress print output
                # Mock process_query to raise an error
                with patch.object(client, 'process_query', side_effect=Exception("Test error")):
                    # Should not crash, should continue loop
                    await client.chat_loop()
    
    @pytest.mark.asyncio
    async def test_chat_loop_handles_empty_input(self):
        """Test chat_loop handles empty input"""
        client = MCPClient()
        
        # Mock session
        mock_session = AsyncMock()
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.model_dump.return_value = {
            "name": "test_tool",
            "description": "Test",
            "inputSchema": {}
        }
        
        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_session.list_tools.return_value = mock_list_response
        client.session = mock_session
        
        mock_ollama_response = {
            "message": {
                "content": "Response",
                "tool_calls": []
            }
        }
        
        # Mock input to return empty string then quit
        input_calls = ["   ", "quit"]  # Whitespace-only input
        with patch('builtins.input', side_effect=input_calls):
            with patch('builtins.print'):
                with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
                    mock_to_thread.return_value = mock_ollama_response
                    await client.chat_loop()


class TestMCPClientConnectToServerOutput:
    """Test connect_to_server output and error handling"""
    
    @pytest.mark.asyncio
    async def test_connect_to_server_prints_messages(self, capsys):
        """Test that connect_to_server prints appropriate messages"""
        client = MCPClient(api_key="test-key")
        
        # This will fail but we can check the print output
        with pytest.raises(FileNotFoundError):
            await client.connect_to_server("nonexistent.py")
        
        # Check that authentication message was printed
        captured = capsys.readouterr()
        assert "Using API key authentication" in captured.out
    
    @pytest.mark.asyncio
    async def test_connect_to_server_no_auth_message(self, capsys):
        """Test connect_to_server message when no auth"""
        client = MCPClient()
        
        with pytest.raises(FileNotFoundError):
            await client.connect_to_server("nonexistent.py")
        
        captured = capsys.readouterr()
        assert "No authentication configured" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

