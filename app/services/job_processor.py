from datetime import datetime, timezone

from sqlalchemy import select

from ..database import SessionLocal
from ..models import Certificate, CertificateStatus, GenerationJob, JobStatus
from .certificate_generator import generate_certificate


def process_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.get(GenerationJob, job_id)
        if not job:
            return

        job.status = JobStatus.PROCESSING.value
        job.updated_at = datetime.now(timezone.utc)
        db.commit()

        certificates = db.scalars(
            select(Certificate).where(Certificate.job_id == job_id)
        ).all()

        for certificate in certificates:
            try:
                output_path = generate_certificate(
                    certificate.id,
                    certificate.recipient_name,
                    job.event_name,
                    job.event_date,
                )

                certificate.status = CertificateStatus.COMPLETED.value
                certificate.file_path = str(output_path)
                certificate.error_message = None
                job.completed_count += 1

            except Exception as exc:
                # One certificate failure must not stop other recipients.
                certificate.status = CertificateStatus.FAILED.value
                certificate.error_message = str(exc)
                job.failed_count += 1

            certificate.updated_at = datetime.now(timezone.utc)
            job.updated_at = datetime.now(timezone.utc)
            db.commit()

        if job.failed_count == 0:
            job.status = JobStatus.COMPLETED.value
        elif job.completed_count == 0:
            job.status = JobStatus.FAILED.value
        else:
            job.status = JobStatus.COMPLETED_WITH_ERRORS.value

        job.updated_at = datetime.now(timezone.utc)
        db.commit()

    except Exception:
        db.rollback()
        job = db.get(GenerationJob, job_id)
        if job:
            job.status = JobStatus.FAILED.value
            job.updated_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()
