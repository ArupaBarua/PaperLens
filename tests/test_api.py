from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db

# Test database

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


Base.metadata.create_all(
    bind=engine
)

client = TestClient(app)

# Session tests

def test_create_session():

    response = client.post(
        "/sessions/",
        json={
            "title": "Test Session"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test Session"
    assert "id" in data


def test_get_all_sessions():

    response = client.get(
        "/sessions/"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_single_session():

    create_response = client.post(
        "/sessions/",
        json={
            "title": "Single Session"
        }
    )

    session_id = create_response.json()["id"]

    response = client.get(
        f"/sessions/{session_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == session_id
    assert data["title"] == "Single Session"


def test_get_nonexistent_session():

    response = client.get(
        "/sessions/999999"
    )

    assert response.status_code == 404


def test_update_session_title():

    create_response = client.post(
        "/sessions/",
        json={
            "title": "Old Title"
        }
    )

    session_id = create_response.json()["id"]

    response = client.put(
        f"/sessions/{session_id}",
        json={
            "title": "New Title"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New Title"


def test_delete_session():

    create_response = client.post(
        "/sessions/",
        json={
            "title": "Delete Me"
        }
    )

    session_id = create_response.json()["id"]

    response = client.delete(
        f"/sessions/{session_id}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/sessions/{session_id}"
    )

    assert response.status_code == 404


def test_delete_nonexistent_session():

    response = client.delete(
        "/sessions/999999"
    )

    assert response.status_code == 404

# Chat history API

def test_get_chat_messages():

    create_response = client.post(
        "/sessions/",
        json={
            "title": "Chat Test"
        }
    )

    session_id = create_response.json()["id"]

    response = client.get(
        f"/chat/{session_id}/messages"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_chat_messages_for_empty_session():

    create_response = client.post(
        "/sessions/",
        json={
            "title": "Empty Chat"
        }
    )

    session_id = create_response.json()["id"]

    response = client.get(
        f"/chat/{session_id}/messages"
    )

    assert response.status_code == 200
    assert response.json() == []

# Root endpoint

def test_home():

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


# Upload API tests

@patch("backend.routes.upload.process_paper")
@patch("backend.routes.upload.upload_paper")
def test_upload_paper(
    mock_upload_paper,
    mock_process_paper
):
    """
    Test that the upload endpoint accepts a PDF
    and returns a successful response.
    """

    mock_paper = MagicMock()

    mock_paper.filename = "test.pdf"
    mock_paper.file_path = "data/test.pdf"
    mock_paper.id = 1
    mock_paper.session_id = 1
    mock_paper.stored_filename = "abc123_test.pdf"

    mock_upload_paper.return_value = mock_paper

    response = client.post(
        "/upload/1",
        files={
            "file": (
                "test.pdf",
                b"%PDF-1.4 fake pdf content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Paper uploaded successfully"
    assert data["paper"]["filename"] == "test.pdf"

    mock_upload_paper.assert_called_once()


@patch("backend.routes.upload.upload_paper")
def test_upload_paper_session_not_found(
    mock_upload_paper
):
    """
    Test that a ValueError from upload_paper
    is converted into a 404 response.
    """

    mock_upload_paper.side_effect = ValueError(
        "Session not found"
    )

    response = client.post(
        "/upload/999999",
        files={
            "file": (
                "test.pdf",
                b"%PDF-1.4 fake pdf content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"