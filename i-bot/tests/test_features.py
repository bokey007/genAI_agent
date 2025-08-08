import pytest
from src.main import app
from src.config import settings

def test_ticket_creation(client):
    settings.TURN_THRESHOLD = 2
    response = client.post("/chat", json={"message": "hello", "user_id": "test_user"})
    assert response.status_code == 200
    data = response.json()
    session_id = data["session_id"]

    response = client.post(
        "/chat", json={"session_id": session_id, "message": "hello again", "satisfied": False, "user_id": "test_user"}
    )
    assert response.status_code == 200

    response = client.post(
        "/chat", json={"session_id": session_id, "message": "hello again", "satisfied": False, "user_id": "test_user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "ticket has been created" in data["response"]

def test_user_history(client):
    response = client.post("/chat", json={"message": "hello", "user_id": "history_user"})
    assert response.status_code == 200

    response = client.get("/history/history_user")
    assert response.status_code == 200
    data = response.json()
    assert "today" in data
    assert len(data["today"]) > 0
