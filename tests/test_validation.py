from unittest.mock import patch


def test_empty_recipients_rejected(client):
    payload = {
        "event_name": "Workshop",
        "event_date": "2026-10-07",
        "recipients": [],
    }

    with patch("app.routes.jobs.process_job"):
        response = client.post("/api/jobs", json=payload)

    assert response.status_code == 422


def test_invalid_email_rejected(client):
    payload = {
        "event_name": "Workshop",
        "event_date": "2026-10-07",
        "recipients": [
            {"name": "Valid Name", "email": "not-an-email"},
        ],
    }

    with patch("app.routes.jobs.process_job"):
        response = client.post("/api/jobs", json=payload)

    assert response.status_code == 422


def test_short_name_rejected(client):
    payload = {
        "event_name": "Workshop",
        "event_date": "2026-10-07",
        "recipients": [
            {"name": "A", "email": "valid@example.com"},
        ],
    }

    with patch("app.routes.jobs.process_job"):
        response = client.post("/api/jobs", json=payload)

    assert response.status_code == 422
