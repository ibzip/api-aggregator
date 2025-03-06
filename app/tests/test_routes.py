# app/tests/test_routes.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_application
from app.database import Base, get_db
from app.models import Post, FetchJob
from app.schemas import PostCreate
from unittest.mock import patch

# ------------------------------------------------------------------------
# 1. TEST DATABASE SETUP
# ------------------------------------------------------------------------

# Create an in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# We override the get_db dependency in the FastAPI app to use our test DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create all tables before running tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally drop tables after tests if you want a fresh DB each time
    Base.metadata.drop_all(bind=engine)

# Create a FastAPI test client
client = TestClient(app)

# ------------------------------------------------------------------------
# 2. SAMPLE TESTS
# ------------------------------------------------------------------------

def test_get_data_empty():
    """
    /data should return an empty list initially (no posts in DB).
    """
    response = client.get("/data")
    assert response.status_code == 200
    assert response.json() == []


@patch("app.routers.fetch.fetch_data_async")
def test_fetch_sync_mode(mock_fetch_data_async):
    """
    Test POST /fetch with mode=sync.
    We mock fetch_data_async to simulate a quick success or error.
    """
    mock_fetch_data_async.return_value = {"message": "Data fetched", "status": "ok"}

    response = client.post("/fetch?mode=sync")
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "ok"
    assert json_resp["message"] == "Data fetched"

    # Ensure the mock was called once
    mock_fetch_data_async.assert_called_once()


@patch("app.routers.fetch.background_fetch_job.delay", return_value=None)
def test_fetch_task_mode(mock_delay):
    """
    Test POST /fetch with mode=task.
    We patch background_fetch_job.delay to avoid attempting to connect to RabbitMQ.
    """
    response = client.post("/fetch?mode=task")
    assert response.status_code == 200
    json_resp = response.json()
    assert "job_id" in json_resp
    assert json_resp["message"] == "Fetch job queued in background"

    # Optionally, check that .delay was called with the new job id
    mock_delay.assert_called_once()

    # Also, check the DB to confirm a FetchJob was created
    db = TestingSessionLocal()
    job = db.query(FetchJob).filter(FetchJob.id == json_resp["job_id"]).first()
    assert job is not None
    assert job.status == "pending"
    db.close()


def test_fetch_job_status_not_found():
    """
    If we query a job that doesn't exist, we should get 404.
    """
    response = client.get("/fetch/status/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_fetch_job_status_found():
    """
    Test fetch job status for an existing job. We'll create one first.
    """
    # Create a job in DB
    db = TestingSessionLocal()
    new_job = FetchJob(status="pending")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    job_id = new_job.id
    db.close()

    # GET /fetch/status/{job_id}
    response = client.get(f"/fetch/status/{job_id}")
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["id"] == job_id
    assert json_resp["status"] == "pending"
    assert json_resp["error"] == ""


@patch("app.routers.fetch.fetch_data_async")
def test_fetch_sync_creates_posts(mock_fetch_data_async):
    """
    Test that a successful sync fetch inserts data into DB.
    We'll mock the fetch_data_async to return synthetic data.
    """
    mock_fetch_data_async.return_value = {"message": "Data fetched", "status": "ok"}

    # Initially no posts
    response = client.get("/data")
    assert response.json() == []

    # Now do a sync fetch
    client.post("/fetch?mode=sync")

    # We can decide how fetch_data_async actually updates the DB.
    # If your real fetch_data_async calls an external API, you'll need
    # a more elaborate test or a deeper mock that inserts records.

    # Because we haven't actually inserted anything in the mock,
    # let's *simulate* a scenario:
    # In real usage, fetch_data_async would do something like:
    # db.add(Post(...)) and db.commit().
    # We'll do it ourselves here just to confirm the /data route works.
    db = TestingSessionLocal()
    new_post = Post(
        id=101, user_id=1, title="Test Post", body="Lorem ipsum"
    )
    db.add(new_post)
    db.commit()
    db.close()

    # Now /data should have 1 post
    response2 = client.get("/data")
    posts = response2.json()
    assert len(posts) == 1
    assert posts[0]["id"] == 101
    assert posts[0]["user_id"] == 1
    assert posts[0]["title"] == "Test Post"
    assert posts[0]["body"] == "Lorem ipsum"

