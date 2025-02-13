# Resume Builder Service

A FastAPI service that handles job post data.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Service

To run the service:

```bash
uvicorn main:app --reload
```

The service will start on `http://localhost:8000`

## API Endpoints

### POST /job_post

Accepts any JSON data in the request body and prints it to the console.

Example request:
```bash
curl -X POST http://localhost:8000/job_post \
  -H "Content-Type: application/json" \
  -d '{"title": "Software Engineer", "company": "Example Corp"}'
``` 