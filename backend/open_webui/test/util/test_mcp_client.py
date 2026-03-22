import pytest
from unittest.mock import AsyncMock, patch

from open_webui.utils.mcp.client import MCPClient

@pytest.mark.asyncio
async def test_mcp_client_declares_elicitation_capabilities_on_connect():
    client = MCPClient()
    
    with patch("open_webui.utils.mcp.client.streamablehttp_client") as mock_streamablehttp_client, \
         patch("open_webui.utils.mcp.client.ClientSession") as mock_client_session_class, \
         patch("open_webui.utils.mcp.client.anyio"):
        
        mock_transport = (AsyncMock(), AsyncMock(), AsyncMock())
        mock_streams_context = AsyncMock()
        mock_streams_context.__aenter__.return_value = mock_transport
        mock_streamablehttp_client.return_value = mock_streams_context
        
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_client_session_class.return_value = mock_session
        
        await client.connect("http://localhost:8000")
        
        mock_session.initialize.assert_awaited_once()
        
        # Verify that ClientSession was constructed with elicitation_callback
        client_session_call_kwargs = mock_client_session_class.call_args.kwargs
        assert client_session_call_kwargs["elicitation_callback"] is not None

@pytest.mark.asyncio
async def test_mcp_client_handle_elicitation_pauses_and_resolves():
    import asyncio
    client = MCPClient()
    
    mock_emit = AsyncMock()
    # Assume a method to register event emission
    client.set_elicitation_handler(mock_emit)
    
    class MockRequest:
        def __init__(self):
            self.id = "elicit-123"
    
    req = MockRequest()
    
    async def resolve_future():
        await asyncio.sleep(0.1)
        client.resolve_elicitation("elicit-123", {"success": True})
        
    asyncio.create_task(resolve_future())
    
    result = await client.handle_elicitation(req)
    
    mock_emit.assert_awaited_once_with(req)
    assert result == {"success": True}
    assert "elicit-123" not in client.pending_elicitations

@pytest.mark.asyncio
async def test_mcp_client_call_tool_intercepts_url_elicitation_error():
    client = MCPClient()
    mock_emit = AsyncMock()
    client.set_elicitation_handler(mock_emit)
    
    mock_session = AsyncMock()
    mock_session.call_tool = AsyncMock()
    
    # We will simulate the McpError by throwing an exception with the appropriate error code
    class McpError(Exception):
        def __init__(self, error):
            self.error = error
            
    # The first call raises -32042
    def call_tool_side_effect(*args, **kwargs):
        if mock_session.call_tool.call_count == 1:
            raise McpError(error={"code": -32042, "message": "URLElicitationRequiredError", "data": {"elicitations": [{"id": "url-1", "url": "https://example.com"}]}})
        
        class MockResult:
            isError = False
            def model_dump(self, mode=None):
                return {"content": {"success": True}}
                
        return MockResult()
        
    mock_session.call_tool.side_effect = call_tool_side_effect
    client.session = mock_session
    
    import asyncio
    async def resolve_future():
        await asyncio.sleep(0.1)
        client.resolve_elicitation("url-1", {"action": "accept"})
        
    asyncio.create_task(resolve_future())
    
    result = await client.call_tool("my_tool", {"arg": "val"})
    
    # It should have called call_tool twice (initial + retry)
    assert mock_session.call_tool.call_count == 2
    # It should have returned the success result
    assert result == {"success": True}
    # It should have emitted the elicitation to the frontend
    assert mock_emit.call_count == 1
    emitted_req = mock_emit.call_args[0][0]
    assert emitted_req["id"] == "url-1"
    assert "https://example.com" in emitted_req["url"]

