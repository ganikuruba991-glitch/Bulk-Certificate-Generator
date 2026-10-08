from unittest.mock import patch


def test_create_generation_job(client):
    payload = {
        "event_name": "Python Workshop",
        "event_date": "2026-10-07",
        "recipients": [
            {"name": "Sangamesh A H", "email": "sangamesh@example.com"},
            {"name": "Rahul Kumar", "email": "rahul@example.com"},
        ],
    }

    # Patch background processing so this test focuses on job creation.
    with patch("app.routes.jobs.process_job"):
        response = client.post("/api/jobs", json=payload)

    assert response.status_code == 202
    body = response.json()
    assert body["event_name"] == "Python Workshop"
    assert body["total_count"] == 2
    assert body["completed_count"] == 0
    assert body["failed_count"] == 0
    assert body["status"] == "PENDING"


def test_get_job(client):
    payload = {
        "event_name": "Backend Training",
        "event_date": "2026-10-07",
        "recipients": [
            {"name": "Test User", "email": "test@example.com"},
        ],
    }

    with patch("app.routes.jobs.process_job"):
        created = client.post("/api/jobs", json=payload).json()

    response = client.get(f"/api/jobs/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_missing_job_returns_404(client):
    response = client.get("/api/jobs/not-a-real-job")
    assert response.status_code == 404
