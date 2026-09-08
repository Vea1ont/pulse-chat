from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from main import app
from security import ALGORITHM, JWT_SECRET_KEY

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"service": "chat", "status": "ok"}

@pytest.fixture
def auth_headers():
    token = jwt.encode({"sub": "1"}, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return {"Authorization": f"Bearer {token}"}

def test_my_chats_nonauthorized():
    response = client.get("/api/v1/chats/")
    assert response.status_code == 401

def test_my_chats_authorized(auth_headers):
    response = client.get("/api/v1/chats/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    

def test_cache_my_chats(auth_headers):
    response = client.get("/api/v1/chats/", headers=auth_headers)
    




def test_send_message_forbidden_for_non_member(auth_headers):
    response = client.post(
        "/api/v1/chats/99999/messages", headers=auth_headers, json={"text": "hi"}
    )
    assert response.status_code == 403


def test_send_message_success(auth_headers):
    response = client.post(
        "/api/v1/chats/", headers=auth_headers, json={"name": "test", "member_ids": []}
    )
    assert response.status_code == 200
    chat_id = response.json()["id"]
    send_message = client.post(
        f"/api/v1/chats/{chat_id}/messages", headers=auth_headers, json={"text": "hi"}
    )
    assert send_message.status_code == 200


def test_history(auth_headers):
    making_chat_for_id = client.post(
        "/api/v1/chats/",
        headers=auth_headers,
        json={"name": "test_history", "member_ids": []},
    )

    assert making_chat_for_id.status_code == 200
    chat_id = making_chat_for_id.json()["id"]
    get_history = client.get(
        f"/api/v1/chats/{chat_id}/messages",
        headers=auth_headers,
    )
    assert get_history.status_code == 200
    assert isinstance(get_history.json(), list)

    not_access_get_history = client.get(
        f"/api/v1/chats/{999999}/messages", headers=auth_headers
    )

    assert not_access_get_history.status_code == 403


def test_get_members(auth_headers):
    making_chat_for_id = client.post(
        "/api/v1/chats/", headers=auth_headers, json={"name": "test", "member_ids": []}
    )
    assert making_chat_for_id.status_code == 200

    chat_id = making_chat_for_id.json()["id"]

    get_members = client.get(f"/api/v1/chats/{chat_id}/members", headers=auth_headers)
    assert get_members.status_code == 200

    not_access_get_members = client.get(
        f"/api/v1/chats/{9999999}/members", headers=auth_headers
    )
    assert not_access_get_members.status_code == 403


def test_blacklist(auth_headers, mock_valkey):
    mock_a, mock_b = mock_valkey
    mock_b.exists = AsyncMock(return_value=1)
    response = client.get(
        "/api/v1/chats/", headers=auth_headers,
    )
    assert response.status_code == 401