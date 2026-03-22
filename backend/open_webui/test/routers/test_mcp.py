import pytest
from fastapi.testclient import TestClient

# We will need to import the router and create a temporary app to test it
from fastapi import FastAPI
from open_webui.routers.mcp import router as mcp_router
from open_webui.utils.mcp.client import MCPClient

import asyncio

app = FastAPI()

# Mock auth
from open_webui.utils.auth import get_verified_user
async def mock_verified_user():
    return {"id": "user-123", "role": "admin"}
app.dependency_overrides[get_verified_user] = mock_verified_user

app.include_router(mcp_router, prefix="/api/v1/mcp")
client = TestClient(app)

def test_mcp_elicitation_endpoint():
    # Setup pending elicitation globally
    mcp_client = MCPClient()
    
    import uuid
    test_id = str(uuid.uuid4())
    
    # We will manually create a future in the instance
    # Assuming MCPClient.pending_elicitations is accessible or class-level
    future = asyncio.Future()
    MCPClient.pending_elicitations[test_id] = future
    
    # Make request to the new endpoint
    response = client.post(f"/api/v1/mcp/elicitation/{test_id}", json={"action": "accept", "data": {"key": "value"}})
    
    assert response.status_code == 200
    assert response.json() == {"status": True}
    
    # Verify future was resolved
    assert future.done()
    assert future.result() == {"action": "accept", "data": {"key": "value"}}
