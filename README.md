# Bulk Certificate Generator

A FastAPI backend that accepts a single request containing many recipients, creates a generation job, generates individual PDF certificates in the background, tracks progress, handles individual failures, and exposes generated certificates for download.

This implementation follows the company assignment requirements.

## Features

- FastAPI backend
- SQLite relational database
- SQLAlchemy ORM
- Pydantic request validation
- Bulk certificate generation
- Background processing with FastAPI BackgroundTasks
- Per-recipient success/failure tracking
- Job progress percentage
- Predefined certificate PDF design
- Certificate download endpoint
- Automated pytest tests
- Swagger/OpenAPI documentation

## Requirements

- Python 3.10+
- pip

## Setup

### 1. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

## API

### Create a bulk generation job

`POST /api/jobs`

Example request:

```json
{
  "event_name": "Python Workshop",
  "event_date": "2026-10-07",
  "recipients": [
    {
      "name": "Sangamesh A H",
      "email": "sangamesh@example.com"
    },
    {
      "name": "Rahul Kumar",
      "email": "rahul@example.com"
    }
  ]
}
```

The endpoint returns HTTP 202 because generation is performed as a background job.

### Check job status

`GET /api/jobs/{job_id}`

Example response:

```json
{
  "id": "job-id",
  "event_name": "Python Workshop",
  "event_date": "2026-10-07",
  "status": "COMPLETED",
  "total_count": 2,
  "completed_count": 2,
  "failed_count": 0,
  "progress_percent": 100.0,
  "certificates": [
    {
      "id": "certificate-id",
      "recipient_name": "Sangamesh A H",
      "recipient_email": "sangamesh@example.com",
      "status": "COMPLETED",
      "file_url": "/api/certificates/certificate-id/download",
      "error_message": null
    }
  ]
}
```

Possible job statuses:

- `PENDING`
- `PROCESSING`
- `COMPLETED`
- `COMPLETED_WITH_ERRORS`
- `FAILED`

### Download a certificate

`GET /api/certificates/{certificate_id}/download`

The API returns the generated PDF.

## Running tests

```bash
pytest -q
```

## Architecture

```text
Client
  |
  | POST /api/jobs
  v
FastAPI
  |
  +--> Pydantic validation
  |
  +--> Create GenerationJob + Certificate records
  |
  +--> BackgroundTasks
          |
          v
      Job Processor
          |
          +--> Generate PDF for each recipient
          |
          +--> Update success/failure
          |
          v
       SQLite
          |
          v
   GET /api/jobs/{id}
          |
          v
   GET /api/certificates/{id}/download
```

## Processing decision

The assignment allows synchronous or background processing. This implementation uses FastAPI BackgroundTasks because certificate generation for a large recipient list can take longer than a normal HTTP request. The API therefore creates the job first and returns immediately with HTTP 202.

Each recipient is processed independently. If one certificate fails, the exception is caught for that certificate and the next recipient continues. The final job status communicates whether all, some, or none of the certificates succeeded.

For a high-scale production deployment, a dedicated task queue such as Celery/RQ with Redis would be a stronger choice than in-process BackgroundTasks. The current implementation intentionally keeps the assignment self-contained and easy to run locally.

## Database design

### generation_jobs

Stores:

- job ID
- event name
- event date
- job status
- total recipients
- completed count
- failed count
- timestamps

### certificates

Stores:

- certificate ID
- parent job ID
- recipient name
- recipient email
- status
- generated PDF path
- error message
- timestamps

## Certificate design

The project uses one predefined PDF certificate layout, as required. The generated certificate includes:

- recipient name
- event name
- event date
- signature area

No template editor or multiple certificate designs are implemented because those are outside the required scope.

## Important implementation decisions

1. **FastAPI** was selected for a lightweight, typed REST API and built-in Swagger documentation.
2. **SQLite** was selected to make local setup simple. The SQLAlchemy layer allows migration to PostgreSQL later.
3. **Pydantic** validates recipient names, emails, event information, and recipient list size before a job is created.
4. **BackgroundTasks** avoids making the client wait for every PDF to finish.
5. **Per-certificate error handling** prevents one failed generation from stopping the remaining recipients.
6. **Progress counters** provide an easy way for a client to monitor the bulk job.
7. **ReportLab** generates the predefined PDF certificate without requiring external office software.

## Future scope

- PostgreSQL for production
- Celery/RQ + Redis for durable distributed background jobs
- Object storage such as S3 for generated files
- Authentication and authorization
- Signed download URLs
- Email delivery
- Batch pagination for very large result sets
- Retry support for failed certificates
- Docker deployment
- Structured logging and monitoring

## Interview preparation

Be prepared to explain:

- Why FastAPI?
- Why background processing?
- Why SQLite?
- How does validation work?
- How does one failed certificate avoid stopping the entire job?
- How is progress calculated?
- How would you scale this to 100,000 recipients?
- Why would you replace BackgroundTasks with Celery/RQ in production?
- How would you store PDFs in cloud storage?

## Learning

The project is designed to demonstrate practical backend concepts: REST APIs, validation, database relationships, background work, file generation, error isolation, automated testing, and API documentation.
