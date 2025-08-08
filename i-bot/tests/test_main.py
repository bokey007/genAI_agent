import pytest
from src.main import app

def test_chat_new_session(client):
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data


def test_chat_existing_session(client):
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    data = response.json()
    session_id = data["session_id"]

    response = client.post(
        "/chat", json={"session_id": session_id, "message": "hello again"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id



