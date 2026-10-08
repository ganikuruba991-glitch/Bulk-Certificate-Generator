from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr


class GenerationJobCreate(BaseModel):
    event_name: str = Field(..., min_length=2, max_length=200)
    event_date: str = Field(..., min_length=1, max_length=50)
    recipients: list[RecipientCreate] = Field(..., min_length=1, max_length=10000)


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipient_name: str
    recipient_email: str
    status: str
    file_url: str | None = None
    error_message: str | None = None


class JobResponse(BaseModel):
    id: str
    event_name: str
    event_date: str
    status: str
    total_count: int
    completed_count: int
    failed_count: int
    progress_percent: float
    certificates: list[CertificateResponse]
