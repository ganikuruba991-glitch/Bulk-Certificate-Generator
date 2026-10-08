from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Certificate, GenerationJob, JobStatus
from ..schemas import GenerationJobCreate, JobResponse
from ..services.job_processor import process_job

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


def serialize_job(job: GenerationJob) -> JobResponse:
    total = job.total_count
    progress = round(
        ((job.completed_count + job.failed_count) / total) * 100, 2
    ) if total else 0.0

    certificates = []
    for cert in job.certificates:
        file_url = (
            f"/api/certificates/{cert.id}/download"
            if cert.file_path and cert.status == "COMPLETED"
            else None
        )
        certificates.append({
            "id": cert.id,
            "recipient_name": cert.recipient_name,
            "recipient_email": cert.recipient_email,
            "status": cert.status,
            "file_url": file_url,
            "error_message": cert.error_message,
        })

    return JobResponse(
        id=job.id,
        event_name=job.event_name,
        event_date=job.event_date,
        status=job.status,
        total_count=job.total_count,
        completed_count=job.completed_count,
        failed_count=job.failed_count,
        progress_percent=progress,
        certificates=certificates,
    )


@router.post("", response_model=JobResponse, status_code=202)
def create_job(
    payload: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job_id = str(uuid4())

    job = GenerationJob(
        id=job_id,
        event_name=payload.event_name.strip(),
        event_date=payload.event_date.strip(),
        status=JobStatus.PENDING.value,
        total_count=len(payload.recipients),
        completed_count=0,
        failed_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    for recipient in payload.recipients:
        job.certificates.append(
            Certificate(
                id=str(uuid4()),
                recipient_name=recipient.name.strip(),
                recipient_email=str(recipient.email),
            )
        )

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(process_job, job_id)
    return serialize_job(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return serialize_job(job)
