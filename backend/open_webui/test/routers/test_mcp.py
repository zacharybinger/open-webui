import pytest
from fastapi.testclient import TestClient

from fastapi import FastAPI
from open_webui.routers.mcp import router as mcp_router
from open_webui.utils.mcp.client import MCPClient
import uuid

import asyncio

app = FastAPI()

# Mock auth
from open_webui.utils.auth import get_verified_user
async def mock_verified_user():
    return {"id": "user-123", "role": "admin"}
app.dependency_overrides[get_verified_user] = mock_verified_user

app.include_router(mcp_router, prefix="/api/v1/mcp")
client = TestClient(app)

def _setup_elicitation_future() -> tuple[str, asyncio.Future]:
    test_id = str(uuid.uuid4())
    future = asyncio.Future()
    MCPClient.pending_elicitations[test_id] = future
    return test_id, future

def test_mcp_elicitation_endpoint_scalar_string():
    test_id, future = _setup_elicitation_future()
    response = client.post(f"/api/v1/mcp/elicitation/{test_id}", json={"action": "accept", "data": "Alice"})
    assert response.status_code == 200
    assert future.result() == {"action": "accept", "content": "Alice"}

def test_mcp_elicitation_endpoint_scalar_integer():
    test_id, future = _setup_elicitation_future()
    response = client.post(f"/api/v1/mcp/elicitation/{test_id}", json={"action": "accept", "data": 42})
    assert response.status_code == 200
    assert future.result() == {"action": "accept", "content": 42}

def test_mcp_elicitation_endpoint_scalar_boolean():
    test_id, future = _setup_elicitation_future()
    response = client.post(f"/api/v1/mcp/elicitation/{test_id}", json={"action": "accept", "data": True})
    assert response.status_code == 200
    assert future.result() == {"action": "accept", "content": True}

def test_mcp_elicitation_endpoint_no_response():
    test_id, future = _setup_elicitation_future()
    # No Response is usually None for data
    response = client.post(f"/api/v1/mcp/elicitation/{test_id}", json={"action": "accept", "data": None})
    assert response.status_code == 200
    assert future.result() == {"action": "accept", "data": None} # data mapped to None stays as payload['data'] is None, but wait, if it's not mapped payload has data: None

def test_mcp_elicitation_endpoint_constrained_options():
    test_id, future = _setup_elicitation_future()
    response = client.post(f"/api/v1/mcp/elicitation/{test_id}", json={"action": "accept", "data": "high"})
    assert response.status_code == 200
    assert future.result() == {"action": "accept", "content": "high"}

def test_mcp_elicitation_endpoint_multi_select():
    test_id, future = _setup_elicitation_future()
    response = client.post(f"/api/v1/mcp/elicitation/{test_id}", json={"action": "accept", "data": ["bug", "feature"]})
    assert response.status_code == 200
    assert future.result() == {"action": "accept", "content": ["bug", "feature"]}

def test_mcp_elicitation_endpoint_structured_responses():
    test_id, future = _setup_elicitation_future()
    response = client.post(f"/api/v1/mcp/elicitation/{test_id}", json={"action": "accept", "data": {"title": "Fix bug", "priority": "high"}})
    assert response.status_code == 200
    assert future.result() == {"action": "accept", "content": {"title": "Fix bug", "priority": "high"}}

def test_mcp_elicitation_endpoint_decline_action():
    test_id, future = _setup_elicitation_future()
    response = client.post(f"/api/v1/mcp/elicitation/{test_id}", json={"action": "decline", "data": None})
    assert response.status_code == 200
    assert future.result() == {"action": "decline", "data": None}
