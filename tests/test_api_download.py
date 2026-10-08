from unittest.mock import patch


def test_certificate_download_before_completion_returns_409(client):
    payload = {
        "event_name": "Workshop",
        "event_date": "2026-10-07",
        "recipients": [
            {"name": "Test User", "email": "test@example.com"},
        ],
    }

    with patch("app.routes.jobs.process_job"):
        created = client.post("/api/jobs", json=payload).json()

    certificate_id = created["certificates"][0]["id"]
    response = client.get(f"/api/certificates/{certificate_id}/download")

    assert response.status_code == 409
