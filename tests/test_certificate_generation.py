from pathlib import Path

from app.services.certificate_generator import generate_certificate


def test_certificate_generation(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.certificate_generator.CERTIFICATE_DIR",
        tmp_path,
    )

    output = generate_certificate(
        "test-certificate-id",
        "Sangamesh A H",
        "Python Workshop",
        "2026-10-07",
    )

    assert output.exists()
    assert output.suffix == ".pdf"
    assert output.stat().st_size > 0


def test_individual_failure_does_not_stop_job(client, monkeypatch):
    from app.database import SessionLocal
    from app.models import Certificate, GenerationJob
    from app.services import job_processor

    payload = {
        "event_name": "Workshop",
        "event_date": "2026-10-07",
        "recipients": [
            {"name": "First User", "email": "first@example.com"},
            {"name": "Second User", "email": "second@example.com"},
        ],
    }

    # Create the job without starting its background task.
    monkeypatch.setattr(job_processor, "generate_certificate", lambda *args: (_ for _ in ()).throw(Exception("simulated failure")))

    from unittest.mock import patch
    with patch("app.routes.jobs.process_job"):
        response = client.post("/api/jobs", json=payload)

    job_id = response.json()["id"]
    job_processor.process_job(job_id)

    db = SessionLocal()
    job = db.get(GenerationJob, job_id)
    certificates = db.query(Certificate).filter(Certificate.job_id == job_id).all()

    assert job.status == "FAILED"
    assert job.failed_count == 2
    assert all(c.status == "FAILED" for c in certificates)
    db.close()
