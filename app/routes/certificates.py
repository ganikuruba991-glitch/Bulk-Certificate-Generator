from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Certificate

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])


@router.get("/{certificate_id}/download")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    certificate = db.get(Certificate, certificate_id)

    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")

    if certificate.status != "COMPLETED" or not certificate.file_path:
        raise HTTPException(
            status_code=409,
            detail="Certificate is not available yet",
        )

    path = Path(certificate.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Certificate file not found")

    safe_name = f"{certificate.recipient_name.replace(' ', '_')}_certificate.pdf"
    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=safe_name,
    )
